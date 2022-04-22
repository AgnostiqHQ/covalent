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

"""Workflow result update functionality."""

import sys
from datetime import datetime, timezone
from multiprocessing import Queue as MPQ
from typing import Dict

from covalent._results_manager import Result

from .dispatch_workflow import dispatch_runnable_tasks
from .dispatcher_logger import logger
from .utils import (
    _post_process,
    are_tasks_running,
    generate_task_result,
    get_parent_id_and_task_id,
    get_result_object_from_result_service,
    is_empty,
    is_sublattice_dispatch_id,
    send_task_update_to_dispatcher,
    send_task_update_to_result_service,
)


def update_workflow_results(
    task_execution_results: Dict, dispatch_id: str, tasks_queue: MPQ
) -> Result:
    """Main update function. Called by the Runner API when there is an update for task
    execution status."""

    latest_result_obj: Result = get_result_object_from_result_service(dispatch_id=dispatch_id)

    # Update the task results
    latest_result_obj._update_node(**task_execution_results)
    send_task_update_to_result_service(dispatch_id, task_execution_results)

    if task_execution_results["status"] == Result.RUNNING:

        if is_sublattice_dispatch_id(latest_result_obj.dispatch_id):

            parent_dispatch_id, task_id = get_parent_id_and_task_id(latest_result_obj.dispatch_id)

            task_result = generate_task_result(
                task_id=task_id,
                status=Result.RUNNING,
            )

            send_task_update_to_dispatcher(parent_dispatch_id, task_result)

        return latest_result_obj

    elif task_execution_results["status"] == Result.FAILED:
        latest_result_obj._status = Result.FAILED

    elif task_execution_results["status"] == Result.CANCELLED:
        latest_result_obj._status = Result.CANCELLED

    elif task_execution_results["status"] == Result.COMPLETED:

        val = tasks_queue.get()

        print(f"Dispatch id: {dispatch_id}, tasks queue ALL CAPS: {val}", file=sys.stderr)

        tasks_queue.put(val)

        # If workflow is completed, post-process result
        if (
            not are_tasks_running(result_obj=latest_result_obj)
            and latest_result_obj.status is not Result.CANCELLED
        ):
            update_completed_workflow(latest_result_obj)

        elif not is_empty(tasks_queue) and latest_result_obj.status is not Result.CANCELLED:
            update_completed_tasks(dispatch_id, tasks_queue, latest_result_obj)

        # Finally if above two functions modified the tasks_queue or the result object
        if (
            is_empty(tasks_queue)
            and not are_tasks_running(result_obj=latest_result_obj)
            and latest_result_obj.status is not Result.CANCELLED
        ):
            update_completed_workflow(latest_result_obj)

    else:
        print(
            f"None of the above with status {task_execution_results['status']} and {is_empty(tasks_queue)}"
        )

    print(
        f"task id: {task_execution_results['node_id']} in dispatch id: {dispatch_id} marked as: {task_execution_results['status']}"
    )

    print(f"Result Object as :\n {latest_result_obj}")

    latest_result_obj = update_workflow_endtime(latest_result_obj)

    return latest_result_obj


def update_workflow_endtime(result_obj: Result) -> Result:
    """Update workflow end time if it has stopped running."""

    if result_obj.status not in [Result.RUNNING, Result.NEW_OBJ]:
        result_obj._end_time = datetime.now(timezone.utc)

    return result_obj


def update_completed_tasks(dispatch_id: str, tasks_queue: MPQ, result_obj: Result) -> Result:
    """Update completed tasks while the parent workflow is still not completed."""

    tasks_order_lod = tasks_queue.get()

    print(
        f"In update_completed_tasks with dispatch_id: {dispatch_id} and tasks_queue: {tasks_order_lod}"
    )

    tasks_dict = tasks_order_lod.pop(0)
    new_dispatch_id, new_tasks_order = zip(*tasks_dict.items())

    new_dispatch_id = new_dispatch_id[0]
    new_tasks_order = new_tasks_order[0]

    if tasks_order_lod:
        tasks_queue.put(tasks_order_lod)
    else:
        # Mark queue as empty
        # Removing tasks_dict from the queue so that the
        # new tasks order which will be sent in the case of
        # same dispatch_ids is an updated one and is
        # not confused with what's in the tasks queue

        # This will also mean that at this moment, tasks_queue
        # does not contain the order in which this last lattice's
        # tasks are going to be executed, which is to maintain uniformity
        # in the conditions in which dispatch_runnable_tasks is called.
        tasks_queue.put(None)

    if new_dispatch_id != dispatch_id:

        next_result_obj = get_result_object_from_result_service(dispatch_id=new_dispatch_id)

        dispatch_runnable_tasks(
            result_obj=next_result_obj, tasks_queue=tasks_queue, task_order=new_tasks_order
        )
    else:

        dispatch_runnable_tasks(
            result_obj=result_obj, tasks_queue=tasks_queue, task_order=new_tasks_order
        )

    return result_obj


def update_completed_workflow(result_obj: Result) -> Result:
    """Update the result for a completed lattice / sublattice workflow."""

    result_obj._result = _post_process(
        lattice=result_obj.lattice,
        task_outputs=result_obj.get_all_node_outputs(),
    )

    result_obj._status = Result.COMPLETED

    print(
        f"Dispatch id: {result_obj.dispatch_id}, REACHED UPDATE COMPLETED WORKFLOW",
        file=sys.stderr,
    )

    if is_sublattice_dispatch_id(result_obj.dispatch_id):
        print(
            f"Dispatch id: {result_obj.dispatch_id}, IS SUBLATTICE",
            file=sys.stderr,
        )

        parent_dispatch_id, task_id = get_parent_id_and_task_id(result_obj.dispatch_id)

        task_result = generate_task_result(
            task_id=task_id,
            end_time=datetime.now(timezone.utc),
            status=Result.COMPLETED,
            output=result_obj.result,
        )

        send_task_update_to_dispatcher(parent_dispatch_id, task_result)

    return result_obj
