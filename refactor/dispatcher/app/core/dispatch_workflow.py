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

import os
from datetime import datetime, timezone
from multiprocessing import Queue as MPQ
from typing import Dict, List, Tuple, Union

import cloudpickle as pickle
import requests
from dotenv import load_dotenv

from covalent._results_manager import Result
from covalent._workflow.transport import _TransportGraph
from covalent.executor import BaseExecutor

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

    # Initialize the result object
    result_obj = init_result_pre_dispatch(result_obj=result_obj)

    # Get the order of tasks to be run
    task_order: List[List] = get_task_order(result_obj=result_obj)

    while task_order:

        # Put the order in tasks_queue to be later used to get runnable tasks
        tasks_queue.put(task_order)

        # To get the runnable tasks
        tasks, functions, input_args, input_kwargs, executors = get_runnable_tasks(
            result_obj=result_obj,
            tasks_queue=tasks_queue,
        )

        unrun_tasks = run_tasks(
            results_dir=result_obj.results_dir,
            dispatch_id=result_obj.dispatch_id,
            task_id_batch=tasks,
            functions=functions,
            input_args=input_args,
            input_kwargs=input_kwargs,
            executors=executors,
        )

        task_order = [unrun_tasks] + tasks_queue.get()

    return result_obj


def get_runnable_tasks(
    result_obj: Result, tasks_queue: MPQ
) -> Tuple[List[int], List[bytes], List[List], List[Dict], List[BaseExecutor]]:
    """Return a list of tasks that can be run and the corresponding executors and input
    parameters."""

    # Getting the first list of task_ids to be run
    tasks_order = tasks_queue.get()
    task_ids = tasks_order.pop(0)

    input_args = []
    input_kwargs = []
    executors = []
    runnable_tasks = []
    non_runnable_tasks = []
    functions = []

    for task_id in task_ids:
        serialized_function = result_obj.lattice.transport_graph.get_node_value(
            task_id, "function"
        )
        task_name = result_obj.lattice.transport_graph.get_node_value(task_id, "name")

        # Get the task inputs from parents and edge names of this node
        task_inputs = get_task_inputs(task_id=task_id, node_name=task_name, result_obj=result_obj)

        executor = result_obj.lattice.transport_graph.get_node_value(task_id, "metadata")[
            "executor"
        ]

        # Check whether the node is a sublattice
        if is_sublattice(task_name):

            # Get the sublattice
            sublattice = serialized_function.get_deserialized()

            # Build the graph for this sublattice
            sublattice.build_graph(*task_inputs["args"], **task_inputs["kwargs"])

            # Construct the result object for this sublattice
            sublattice_result_obj = Result(
                lattice=sublattice,
                results_dir=sublattice.metadata["results_dir"],
                dispatch_id=f"{result_obj.dispatch_id}:{task_id}",
            )

            # Serialize its transport graph
            sublattice_result_obj._lattice.transport_graph = (
                sublattice_result_obj._lattice.transport_graph.serialize()
            )

            # Update the status of this node in result object
            result_obj._update_node(
                node_id=task_id,
                start_time=datetime.now(timezone.utc),
                status=Result.RUNNING,
            )

            sublattice_task_queue = MPQ()

            dispatch_workflow(result_obj=sublattice_result_obj, tasks_queue=sublattice_task_queue)

            # sublattice_task_order = get_task_order(sublattice_result_obj)
            # tasks_order = sublattice_task_order + tasks_order
            # tasks_queue.put(tasks_order)
            # get_runnable_tasks(result_obj=sublattice_result_obj, tasks_queue=tasks_queue)

        elif is_runnable_task(task_id, result_obj):
            # If the task is runnable, i.e, its parents have completed execution

            # Check whether task is of non-executable type
            result_obj, is_executable = preprocess_transport_graph(task_id, task_name, result_obj)

            # If task is not executable then continue loop to next task
            if not is_executable:
                continue

            # Add the details of this task to respective lists
            runnable_tasks.append(task_id)
            functions.append(serialized_function)
            input_args.append(task_inputs["args"])
            input_kwargs.append(task_inputs["kwargs"])
            executors.append(executor)

        else:
            # If the task is not runnable, i.e, its parents have not completed execution
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


def send_task_list_to_runner(dispatch_id, tasks_list):

    # Example tasks_list:
    # tasks_list = [
    #     {
    #         "task_id": 0,
    #         "func": result_object.lattice.transport_graph.get_node_value(0, "function"),
    #         "args": [2 + 2],
    #         "kwargs": {},
    #         "executor": result_object.lattice.transport_graph.get_node_value(0, "metadata")[
    #             "executor"
    #         ],
    #         "results_dir": result_object.results_dir,
    #     },
    #     {
    #         "task_id": 2,
    #         "func": result_object.lattice.transport_graph.get_node_value(2, "function"),
    #         "args": [2, 10],
    #         "kwargs": {},
    #         "executor": result_object.lattice.transport_graph.get_node_value(2, "metadata")[
    #             "executor"
    #         ],
    #         "results_dir": result_object.results_dir,
    #     },
    # ]
    # response = requests.post(url=url_endpoint, files={"tasks": pickle.dumps(tasks_list)})

    # Set the url endpoint
    url_endpoint = f"http://localhost:8000/api/v0/workflow/{dispatch_id}/tasks"

    # Send the tasks list as file
    response = requests.post(url=url_endpoint, files={"tasks": pickle.dumps(tasks_list)})

    # Raise error if occurred
    response.raise_for_status()

    return response.json()["left_out_task_ids"]


def run_tasks(
    results_dir: str,
    dispatch_id: str,
    task_id_batch: List[int],
    functions: List[bytes],
    input_args: List[List],
    input_kwargs: List[Dict],
    executors: List[Union[bytes, str]],
):
    """Ask Runner to execute tasks - get back True (False) if resources are (not) available.

    The Runner might not have resources available to pick up the batch of tasks. In that case,
    this function continues to try running the tasks until the runner becomes free.
    """

    tasks_list = [
        {
            "task_id": task_id,
            "func": func,
            "args": args,
            "kwargs": kwargs,
            "executor": executor,
            "results_dir": results_dir,
        }
        for task_id, func, args, kwargs, executor in zip(
            task_id_batch, functions, input_args, input_kwargs, executors
        )
    ]

    return send_task_list_to_runner(dispatch_id=dispatch_id, tasks_list=tasks_list)


def is_runnable_task(task_id: int, results_obj: Result) -> bool:
    """Return status whether the task can be run."""

    parent_node_ids = results_obj.lattice.transport_graph.get_dependencies(task_id)

    return all(
        results_obj._get_node_status(node_id) == Result.COMPLETED for node_id in parent_node_ids
    )
