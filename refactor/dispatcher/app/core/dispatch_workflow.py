# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.


"""Workflow dispatch functionality."""

import json
import os
from multiprocessing import Queue as MPQ
from typing import Dict, List, Tuple

import cloudpickle as pickle
import requests
from dotenv import load_dotenv

from covalent._dispatcher_plugins import BaseDispatcher
from covalent._results_manager import Result
from covalent._workflow.transport import _TransportGraph

from .utils import get_task_inputs, get_task_order, is_sublattice, preprocess_transport_graph

load_dotenv()


BASE_URI = os.environ.get("BASE_URI")


def dispatch_workflow(result_obj: Result, tasks_queue: MPQ) -> Result:
    """Responsible for starting off the workflow dispatch."""

    if result_obj.status == Result.NEW_OBJ:
        result_obj._status = Result.RUNNING
        result_obj = start_dispatch(result_obj=result_obj, tasks_queue=tasks_queue)

    elif result_obj.status == Result.COMPLETED:
        # TODO - Redispatch workflow for reproducibility

        pass

    elif result_obj.status == Result.CANCELLED:
        # TODO - Redispatch cancelled workflow

        # Change status to running if we want to redeploy this workflow
        result_obj._status = Result.RUNNING

        # TODO - Redispatch tasks

    elif result_obj.status == Result.FAILED:
        # TODO - Redispatch failed workflow

        pass

    return result_obj


def start_dispatch(result_obj: Result, tasks_queue: MPQ) -> Result:
    """Responsible for preprocessing the tasks, and sending the tasks for execution to the
    Runner API in batches. One of the underlying principles is that the Runner API doesn't
    interact with the Data API."""

    # TODO - Clear queue?

    result_obj = init_result_pre_dispatch(result_obj=result_obj)
    task_order: List[List] = get_task_order(result_obj=result_obj)
    tasks_queue.put(task_order)
    tasks, functions, input_args, input_kwargs, executors = get_runnable_tasks(
        result_obj, tasks_queue
    )
    run_tasks(
        results_dir=result_obj.results_dir,
        dispatch_id=result_obj.dispatch_id,
        task_id_batch=tasks,
        functions=functions,
        input_args=input_args,
        input_kwargs=input_kwargs,
        executors=executors,
    )
    return result_obj


def get_runnable_tasks(
    result_obj: Result, tasks_queue: MPQ
) -> Tuple[List[int], List[bytes], List[List], List[Dict], List[BaseDispatcher]]:
    """Return a list of tasks that can be run and the corresponding executors and input
    parameters."""

    tasks_order = tasks_queue.get()
    tasks = tasks_order.pop(0)

    input_args = []
    input_kwargs = []
    executors = []
    runnable_tasks = []
    non_runnable_tasks = []
    functions = []

    for task_id in tasks:
        serialized_function = result_obj.lattice.transport_graph.get_node_value(
            task_id, "function"
        )
        task_name = result_obj.lattice.transport_graph.get_node_value(task_id, "name")
        task_inputs = get_task_inputs(task_id=task_id, node_name=task_name, result_obj=result_obj)
        executor = result_obj.lattice.transport_graph.get_node_value(task_id, "metadata")[
            "executor"
        ]

        if is_sublattice(task_name):
            sublattice = serialized_function.get_deserialized()
            sublattice.build_graph(task_inputs)
            sublattice_result_obj = Result(
                lattice=sublattice,
                results_dir=result_obj.lattice.metadata["results_dir"],
                dispatch_id=f"{result_obj.dispatch_id}:{task_id}",
            )
            result_obj.lattice.transport_graph.set_node_value(
                node_key=task_id, value_key="status", value=Result.RUNNING
            )
            sublattice_task_order = get_task_order(sublattice_result_obj)
            tasks_order = sublattice_task_order + tasks_order
            tasks_queue.put(tasks_order)
            get_runnable_tasks(result_obj=sublattice_result_obj, tasks_queue=tasks_queue)

        elif is_runnable_task(task_id, result_obj, tasks_queue):
            runnable_tasks.append(task_id)
            preprocess_transport_graph(task_id, task_name, result_obj)
            input_args.append(task_inputs["args"])
            input_kwargs.append(task_inputs["kwargs"])
            executors.append(executor)
            functions.append(serialized_function)

        else:
            non_runnable_tasks.append(task_id)

    if non_runnable_tasks:
        tasks_order = [non_runnable_tasks] + tasks_order
        tasks_queue.put(tasks_order)

    return runnable_tasks, functions, input_args, input_kwargs, executors


def init_result_pre_dispatch(result_obj: Result):
    """Initialize the result object transport graph before it is dispatched for execution."""

    transport_graph = _TransportGraph()
    transport_graph.deserialize(result_obj.lattice.transport_graph)
    result_obj._lattice.transport_graph = transport_graph
    result_obj._initialize_nodes()
    return result_obj


def run_tasks(
    results_dir: str,
    dispatch_id: str,
    task_id_batch: List[int],
    functions: List[bytes],
    input_args: List[List],
    input_kwargs: List[Dict],
    executors: List[bytes],
):
    """Ask Runner to execute tasks - get back True (False) if resources are (not) available.

    The Runner might not have resources available to pick up the batch of tasks. In that case,
    this function continues to try running the tasks until the runner becomes free.
    """

    request_body = [
        pickle.dumps(
            {
                "task_id": task_id,
                "func": func,
                "args": args,
                "kwargs": kwargs,
                "executor": executor,
                "results_dir": results_dir,
            }
        )
        for task_id, func, args, kwargs, executor in zip(
            task_id_batch, functions, input_args, input_kwargs, executors
        )
    ]

    response = requests.post(
        f"{BASE_URI}/api/v0/workflow/{dispatch_id}/tasks",
        data=pickle.dumps(request_body),
    )
    response.raise_for_status()

    return json.loads(response.text)["left_out_task_ids"]


def is_runnable_task(task_id: int, results_obj: Result, tasks_queue: MPQ) -> bool:
    """Return status whether the task can be run."""

    parent_node_ids = results_obj.lattice.transport_graph.get_dependencies(task_id)

    for node_id in parent_node_ids:
        if results_obj._get_node_status(node_id) != Result.COMPLETED:
            return False

    return True
