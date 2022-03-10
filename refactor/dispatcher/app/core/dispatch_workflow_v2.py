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

from multiprocessing import Queue as MPQ
from typing import Dict, List, Tuple

import cloudpickle as pickle

from covalent._dispatcher_plugins import BaseDispatcher
from covalent._results_manager import Result
from covalent._workflow.transport import _TransportGraph

from .utils import (
    get_sublattice,
    get_task_inputs,
    get_task_order,
    is_sublattice,
    preprocess_transport_graph,
)


def _dispatch_workflow(result_obj: Result, tasks_queue: MPQ) -> Result:
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

    result_obj = init_result_pre_dispatch(result_obj=result_obj)
    task_order: List[List] = get_task_order(result_obj=result_obj)
    tasks_queue.put(task_order)
    tasks, input_args, executors = _get_runnable_tasks(result_obj, tasks_queue)
    _run_task(
        result_obj=result_obj,
        task_id_batch=tasks,
        pickled_input_args=pickle.dumps(input_args),
        pickled_executors=pickle.dumps(executors),
    )
    return result_obj


def _get_runnable_tasks(
    result_obj: Result, tasks_queue: MPQ
) -> Tuple[List[int], List[Dict], List[BaseDispatcher]]:
    """Return a list of tasks that can be run and the corresponding executors and input
    parameters."""

    if tasks_queue.empty():
        return [], [], []

    tasks_order = tasks_queue.get()
    tasks = tasks_order.pop(0)

    input_args = []
    executors = []
    runnable_tasks = []
    non_runnable_tasks = []

    for task_id in tasks:
        task_name = result_obj.lattice.transport_graph.get_node_value(task_id, "name")
        task_inputs = get_task_inputs(task_id=task_id, node_name=task_name, result_obj=result_obj)
        executor = result_obj.lattice.transport_graph.get_node_value(task_id, "metadata")[
            "executor"
        ]

        if is_sublattice(task_name):
            sublattice = get_sublattice(task_id, result_obj)
            sublattice.build_graph(task_inputs)
            sublattice_result_obj = Result(
                lattice=sublattice,
                results_dir=result_obj.lattice.metadata["results_dir"],
                dispatch_id=f"{result_obj.dispatch_id}:{task_id}",
            )
            result_obj.lattice.transport_graph.set_node_value(
                node_key=task_id, value_key="status", value=Result.RUNNING
            )
            sublattice_task_queue = MPQ()
            sublattice_task_order = get_task_order(sublattice_result_obj)
            sublattice_task_queue.put(sublattice_task_order)
            _get_runnable_tasks(
                result_obj=sublattice_result_obj, tasks_queue=sublattice_task_queue
            )

        elif _is_runnable_task(task_id, result_obj, tasks_queue):
            runnable_tasks.append(task_id)
            preprocess_transport_graph(task_id, task_name, result_obj)
            input_args.append(task_inputs)
            executors.append(executor)

        else:
            non_runnable_tasks.append(task_id)

    if non_runnable_tasks:
        tasks = non_runnable_tasks + tasks
        tasks_queue.put(tasks)

    # TODO - Insert dispatch id?

    return runnable_tasks, input_args, executors


def init_result_pre_dispatch(result_obj: Result):
    """Initialize the result object transport graph before it is dispatched for execution."""

    transport_graph = _TransportGraph()
    transport_graph.deserialize(result_obj.lattice.transport_graph)
    result_obj._lattice.transport_graph = transport_graph
    result_obj._initialize_nodes()
    return result_obj


def _run_task(
    result_obj: Result,
    task_id_batch: List[int],
    pickled_input_args: bytes,
    pickled_executors: bytes,
):
    """Ask Runner to execute tasks - get back True (False) if resources are (not) available.

    The Runner might not have resources available to pick up the batch of tasks. In that case,
    this function continues to try running the tasks until the runner becomes free.
    """

    pass


def _is_runnable_task(task_id, results_obj, tasks_queue) -> bool:
    """Return status whether the task can be run"""
    pass
