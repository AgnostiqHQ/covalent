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

from datetime import datetime, timezone
from multiprocessing import Queue as MPQ
from typing import Dict, List, Tuple, Union

from app.core.dispatcher_logger import logger
from app.core.utils import send_result_object_to_result_service, send_task_list_to_runner

from covalent._results_manager import Result
from covalent._workflow.transport import _TransportGraph
from covalent.executor import BaseExecutor

from .utils import get_task_inputs, get_task_order, is_sublattice, preprocess_transport_graph


def dispatch_workflow(result_obj: Result, tasks_queue: MPQ) -> Result:
    """Responsible for starting off the workflow dispatch."""

    # logger.warning(f"Inside dispatch_workflow with dispatch_id {result_obj.dispatch_id}")

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


def dispatch_runnable_tasks(result_obj: Result, tasks_queue: MPQ, task_order: List[List]) -> None:
    """Get runnable tasks and dispatch them to the Runner API. Put the tasks that weren't picked up by the Runner API back in the queue."""

    # To get the runnable tasks from first task order list
    # Sending the tasks_queue as well to handle the case of sublattices
    tasks, functions, input_args, input_kwargs, executors, next_tasks_order = get_runnable_tasks(
        result_obj=result_obj,
        tasks_order=task_order,
        tasks_queue=tasks_queue,
    )

    # The next set of tasks that can be run afterwards
    # This is the case of a new dispatch id in the list of dictionaries
    if next_tasks_order:
        if is_empty(tasks_queue):
            tasks_queue.put([{result_obj.dispatch_id: next_tasks_order}])
        else:
            tasks_queue.put([{result_obj.dispatch_id: next_tasks_order}] + tasks_queue.get())

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

    # Will add those unrun tasks back to the tasks_queue
    final_task_order = tasks_queue.get()
    if unrun_tasks:
        if final_task_order is not None:
            final_task_order[0][result_obj.dispatch_id] = [unrun_tasks] + final_task_order[0][
                result_obj.dispatch_id
            ]
        else:
            final_task_order = [{result_obj.dispatch_id: [unrun_tasks]}]

    # Put the task order back into the queue
    tasks_queue.put(final_task_order)


def convert_lol(dispatch_id: str, lol: List[List]):

    # How it is: [[3, 4], [1, 2, 5], [6, 7, 8]]
    # How it should be: [{d_id_1:[[4]]}, {d_id_2:[[1, 2, 5]]}]

    pass


def is_empty(mp_queue: MPQ):
    if elem := mp_queue.get():
        mp_queue.put(elem)
        return True
    else:
        mp_queue.put(None)
        return False


def start_dispatch(result_obj: Result, tasks_queue: MPQ) -> Result:
    """Responsible for preprocessing the tasks, and sending the tasks for execution to the
    Runner API in batches. One of the underlying principles is that the Runner API doesn't
    interact with the Data API."""

    # logger.warning(f"Inside start_dispatch with dispatch_id {result_obj.dispatch_id}")

    # Initialize the result object
    result_obj = init_result_pre_dispatch(result_obj=result_obj)

    # Send the initialized result to the result service
    send_result_object_to_result_service(result_object=result_obj)

    # Get the order of tasks to be run
    task_order: List[List] = get_task_order(result_obj=result_obj)

    # logger.warning(f"task_order: {task_order}")
    dispatch_runnable_tasks(result_obj, tasks_queue, task_order)

    # logger.warning(f"Inside start_dispatch with finished dispatch_id {result_obj.dispatch_id}")

    send_result_object_to_result_service(result_obj)

    return result_obj


def get_runnable_tasks(
    result_obj: Result,
    tasks_order: List[List],
    tasks_queue: MPQ,
) -> Tuple[List[int], List[bytes], List[List], List[Dict], List[BaseExecutor]]:
    """Return a list of tasks that can be run and the corresponding executors and input
    parameters."""

    # logger.warning(f"In get_runnable_tasks task_order after get: {tasks_order}")

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
                results_dir=result_obj.lattice.metadata["results_dir"],
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

            # Dispatch the sublattice recursively
            dispatch_workflow(result_obj=sublattice_result_obj, tasks_queue=tasks_queue)

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

    # If there are non runnable tasks then add them as well to next task order list else
    # only keep the node lists already present in tasks_order
    next_tasks_order = [non_runnable_tasks] + tasks_order if non_runnable_tasks else tasks_order

    # logger.warning(f"In get_runnable_tasks task_order after put: {next_tasks_order}")

    return runnable_tasks, functions, input_args, input_kwargs, executors, next_tasks_order


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
