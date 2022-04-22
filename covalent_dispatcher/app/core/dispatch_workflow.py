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

import sys
from datetime import datetime, timezone
from multiprocessing import Queue as MPQ
from queue import Empty
from typing import Dict, List, Tuple, Union

from app.core.dispatcher_logger import logger
from app.core.utils import (
    get_parent_id_and_task_id,
    is_empty,
    send_result_object_to_result_service,
    send_task_list_to_runner,
)

from covalent._results_manager import Result
from covalent._workflow.transport import _TransportGraph
from covalent.executor import BaseExecutor

from .utils import get_task_inputs, get_task_order, is_sublattice, preprocess_transport_graph


def dispatch_workflow(result_obj: Result, tasks_queue: MPQ) -> Result:
    """Responsible for starting off the workflow dispatch."""

    # logger.warning(f"Inside dispatch_workflow with dispatch_id {result_obj.dispatch_id}")

    if result_obj.status == Result.NEW_OBJ:
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

    # logger.warning(f"Inside start_dispatch with dispatch_id {result_obj.dispatch_id}")

    # Change result status to running and set workflow execution start time.
    result_obj._status = Result.RUNNING
    result_obj._start_time = datetime.now(timezone.utc)

    # Initialize the result object
    result_obj = init_result_pre_dispatch(result_obj)

    # Send the initialized result to the result service
    send_result_object_to_result_service(result_obj)

    # Get the order of tasks to be run
    task_order: List[List] = get_task_order(result_obj)

    logger.warning(f"task_order: {task_order}")
    dispatch_runnable_tasks(result_obj, tasks_queue, task_order)

    send_result_object_to_result_service(result_obj)

    return result_obj


def dispatch_runnable_tasks(result_obj: Result, tasks_queue: MPQ, task_order: List[List]) -> None:
    """Get runnable tasks and dispatch them to the Runner API. Put the tasks that weren't picked
    up by the Runner API back in the queue."""

    print(
        f"Dispatch id: {result_obj.dispatch_id}, tasks order: {task_order}",
        file=sys.stderr,
    )

    val = tasks_queue.get()

    print(
        f"Dispatch id: {result_obj.dispatch_id}, tasks queue initial: {val}",
        file=sys.stderr,
    )

    tasks_queue.put(val)

    # To get the runnable tasks from first task order list
    # Sending the tasks_queue as well to handle the case of sublattices
    tasks, functions, input_args, input_kwargs, executors, next_tasks_order = get_runnable_tasks(
        result_obj=result_obj,
        tasks_order=task_order,
        tasks_queue=tasks_queue,
    )

    logger.warning(f"In dispatch_runnable_tasks with tasks: {tasks}")

    logger.warning(f"Set of next tasks to be run {next_tasks_order}")

    print(
        f"Dispatch id: {result_obj.dispatch_id}, will try to run these nodes: {tasks}",
        file=sys.stderr,
    )

    # The next set of tasks that can be run afterwards
    # This is the case of a new dispatch id in the list of dictionaries
    if next_tasks_order:
        if is_empty(tasks_queue):
            v = tasks_queue.get()
            logger.warning(f"LETS SEE IF TASKS QUEUE IS EMPTY ITS VAL IS: {v}")
            tasks_queue.put([{result_obj.dispatch_id: next_tasks_order}])
        else:

            all_tasks_lod = tasks_queue.get()

            # Checking if current dispatch id is a parent of last
            # dispatch id in the tasks queue
            last_dispatch_id = str(list(all_tasks_lod[0])[0])
            parent_id, _ = get_parent_id_and_task_id(last_dispatch_id)

            if parent_id == result_obj.dispatch_id:
                all_tasks_lod = all_tasks_lod + [{result_obj.dispatch_id: next_tasks_order}]
            else:
                all_tasks_lod = [{result_obj.dispatch_id: next_tasks_order}] + all_tasks_lod

            tasks_queue.put(all_tasks_lod)

    # Tasks which were not able to run
    unrun_tasks = run_tasks(
        results_dir=result_obj.results_dir,
        dispatch_id=result_obj.dispatch_id,
        task_id_batch=tasks,
        functions=functions,
        input_args=input_args,
        input_kwargs=input_kwargs,
        executors=executors,
    )

    print(f"Dispatch id: {result_obj.dispatch_id}, unrun_tasks: {unrun_tasks}", file=sys.stderr)

    # Add unrun tasks back to the tasks_queue
    final_task_order = tasks_queue.get()

    print(
        f"Dispatch id: {result_obj.dispatch_id}, intermediate_task_order: {final_task_order}",
        file=sys.stderr,
    )

    if unrun_tasks:
        if final_task_order is not None:
            print(f"unrun tasks: {unrun_tasks}")
            print(f"final task order: {final_task_order}")

            if final_task_order[0].get(result_obj.dispatch_id):
                final_task_order[0][result_obj.dispatch_id] = [unrun_tasks] + final_task_order[0][
                    result_obj.dispatch_id
                ]
            else:
                new_dict = {result_obj.dispatch_id: [unrun_tasks]}
                final_task_order = [new_dict] + final_task_order
        else:
            final_task_order = [{result_obj.dispatch_id: [unrun_tasks]}]

    logger.warning(f"Tasks which are yet to execute {final_task_order}")

    try:
        logger.warning(f"Before we put in final_task_order {tasks_queue.get_nowait()}")

    except Empty:
        logger.warning("Before we put in final_task_order, its empty")

    # Put the task order back into the queue
    tasks_queue.put(final_task_order)

    print(
        f"Dispatch id: {result_obj.dispatch_id}, tasks queue final: {final_task_order}",
        file=sys.stderr,
    )


def get_runnable_tasks(
    result_obj: Result,
    tasks_order: List[List],
    tasks_queue: MPQ,
) -> Tuple[List[int], List[bytes], List[List], List[Dict], List[BaseExecutor], List[List[int]]]:
    """Return a list of tasks that can be run and the corresponding executors and input
    parameters."""

    # logger.warning(f"In get_runnable_tasks task_order after get: {tasks_order}")

    # print(
    #     f"GET_RUNNABLE_TASKS - dispatch_id: {result_obj.dispatch_id}, tasks_order: {tasks_order}",
    #     file=sys.stderr,
    # )

    task_ids = tasks_order.pop(0)

    # print(
    #     f"GET_RUNNABLE_TASKS -  dispatch_id: {result_obj.dispatch_id}, task_ids: {task_ids}",
    #     file=sys.stderr,
    # )

    input_args = []
    input_kwargs = []
    executors = []
    runnable_tasks = []
    non_runnable_tasks = []
    functions = []

    for task_id in task_ids:

        task_name = result_obj._get_node_name(task_id)

        # Check whether task is of non-executable type
        result_obj, is_executable = preprocess_transport_graph(task_id, task_name, result_obj)

        if not is_executable:
            if task_id == task_ids[-1] and not runnable_tasks and tasks_order:
                return get_runnable_tasks(
                    result_obj=result_obj, tasks_order=tasks_order, tasks_queue=tasks_queue
                )
            continue

        serialized_function = result_obj.transport_graph.get_node_value(task_id, "function")

        # Get the task inputs from parents and edge names of this node
        task_inputs = get_task_inputs(task_id=task_id, node_name=task_name, result_obj=result_obj)

        executor = result_obj.transport_graph.get_node_value(task_id, "metadata")["executor"]

        # Check whether the node is a sublattice
        if is_sublattice(task_name):

            print("INSIDE SUBLATTICE", file=sys.stderr)

            # Get the sublattice
            sublattice = serialized_function.get_deserialized()

            # Build the graph for this sublattice
            sublattice.build_graph(*task_inputs["args"], **task_inputs["kwargs"])

            # Construct the result object for this sublattice
            sublattice_result_obj = Result(
                lattice=sublattice,
                results_dir=result_obj.lattice.metadata["results_dir"],
                dispatch_id=f"{result_obj.dispatch_id}:{task_id}",
            )

            print(
                f"TASKS ORDER IN SUBLATTICE CONDITION: {get_task_order(sublattice_result_obj)}",
                file=sys.stderr,
            )

            # Dispatch the sublattice recursively
            dispatch_workflow(result_obj=sublattice_result_obj, tasks_queue=tasks_queue)

        elif is_runnable_task(task_id, result_obj):

            # Add the details of this task to respective lists
            runnable_tasks.append(task_id)
            functions.append(serialized_function)
            input_args.append(task_inputs["args"])
            input_kwargs.append(task_inputs["kwargs"])
            executors.append(executor)

        else:
            # If the task is not runnable, i.e, its parents have not completed execution
            non_runnable_tasks.append(task_id)

    # If there are non runnable tasks then add them as well to next task order list else
    # only keep the node lists already present in tasks_order
    next_tasks_order = [non_runnable_tasks] + tasks_order if non_runnable_tasks else tasks_order

    # logger.warning(f"In get_runnable_tasks task_order after put: {next_tasks_order}")

    return runnable_tasks, functions, input_args, input_kwargs, executors, next_tasks_order


def init_result_pre_dispatch(result_obj: Result):
    """Initialize the result object transport graph before it is dispatched for execution."""
    result_obj._initialize_nodes()
    return result_obj


def run_tasks(
    results_dir: str,
    dispatch_id: str,
    task_id_batch: List[int],
    functions: List[bytes],
    input_args: List[List],
    input_kwargs: List[Dict],
    executors: List[Union[bytes, str]],
) -> List[int]:
    """Request Runner to execute tasks.

    The Runner might not have resources available to pick up the full batch of tasks. In that case,
    this function returns the list of task ids that were not picked up.
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


def is_runnable_task(task_id: int, result_obj: Result) -> bool:
    """Return status whether the task can be run based on whether the parent tasks have finished
    executing."""

    parent_node_ids: List[int] = result_obj.transport_graph.get_dependencies(task_id)

    return all(
        result_obj._get_node_status(node_id) == Result.COMPLETED for node_id in parent_node_ids
    )
