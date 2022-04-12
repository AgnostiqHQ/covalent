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
    get_result_object_from_result_service,
    is_empty,
    is_sublattice_dispatch_id,
    send_result_object_to_result_service,
    send_task_update_to_dispatcher,
)


def update_workflow_results(
    task_execution_results: Dict, dispatch_id: str, tasks_queue: MPQ
) -> Result:
    """Main update function. Called by the Runner API when there is an update for task
    execution status."""

    latest_result_obj: Result = get_result_object_from_result_service(dispatch_id=dispatch_id)

    logger.warning(f"Updating with task as {task_execution_results}")

    # Update the task results
    latest_result_obj._update_node(**task_execution_results)

    if task_execution_results["status"] == Result.RUNNING:

        return latest_result_obj

    elif task_execution_results["status"] == Result.FAILED:

        latest_result_obj._status = Result.FAILED

    elif task_execution_results["status"] == Result.CANCELLED:

        latest_result_obj._status = Result.CANCELLED

    # If workflow is completed, post-process result
    elif not are_tasks_running(result_obj=latest_result_obj):

        latest_result_obj = _update_completed_workflow(result_obj=latest_result_obj)

    elif task_execution_results["status"] == Result.COMPLETED and not is_empty(tasks_queue):

        _update_completed_task(task_execution_results, latest_result_obj, tasks_queue, dispatch_id)

    else:
        logger.warning(
            f"None of the above with status {task_execution_results['status']} and {is_empty(tasks_queue)}"
        )

    latest_result_obj = _update_execution_endtime(latest_result_obj)

    return latest_result_obj


def _update_execution_endtime(result_obj: Result):
    """Update the workflow execution end time."""

    if result_obj.status != Result.RUNNING:
        result_obj._end_time = datetime.now(timezone.utc)


def _update_completed_workflow(result_obj: Result, task_execution_results: Dict):
    """Update after sublattice / lattice workflow is completed."""

    logger.warning(
        f"Post processing result with status {task_execution_results['status']} started"
    )

    result_obj._result = _post_process(
        lattice=result_obj.lattice,
        task_outputs=result_obj.get_all_node_outputs(),
    )

    result_obj._status = Result.COMPLETED

    logger.warning(f"Result object looks like this: {result_obj}")

    logger.warning(f"Post processing result with status {task_execution_results['status']} done")

    if is_sublattice_dispatch_id(result_obj.dispatch_id):

        splits = result_obj.dispatch_id.split(":")
        parent_dispatch_id, task_id = ":".join(splits[:-1]), splits[-1]

        task_result = generate_task_result(
            task_id=int(task_id),
            end_time=datetime.now(timezone.utc),
            status=Result.COMPLETED,
            output=result_obj.result,
        )

        logger.warning(f"PARENT ID: {parent_dispatch_id}")
        logger.warning(f"TASK ID: {task_id}")

        send_task_update_to_dispatcher(parent_dispatch_id, task_result)

    return result_obj


def _update_completed_task(
    task_execution_results: Dict, result_obj: Result, tasks_queue: MPQ, dispatch_id: str
):
    """Update after a task is completed but the workflow is not completed."""

    logger.warning(f"Will send next list of tasks, status: {task_execution_results['status']}")

    tasks_order_lod = tasks_queue.get()

    logger.warning(f"tasks_order_lod is this: {tasks_order_lod}")

    tasks_dict = tasks_order_lod.pop(0)
    new_dispatch_id, new_tasks_order = zip(*tasks_dict.items())

    new_dispatch_id = new_dispatch_id[0]
    new_tasks_order = new_tasks_order[0]

    if tasks_order_lod:
        logger.warning("tasks_order_lod is not empty")
        tasks_queue.put(tasks_order_lod)
    else:
        logger.warning("tasks_order_lod is empty")
        # Mark queue as empty
        tasks_queue.put(None)

    logger.warning(f"NEW DISPATCH_ID: {new_dispatch_id}, OLD DISPATCH_ID: {dispatch_id}")

    if new_dispatch_id != dispatch_id:
        logger.warning("CASE OF SUBLATTICE WITH DIFFERING DISPATCH IDS")

        next_result_obj = get_result_object_from_result_service(dispatch_id=new_dispatch_id)

        dispatch_runnable_tasks(
            result_obj=next_result_obj, tasks_queue=tasks_queue, task_order=new_tasks_order
        )

        logger.warning("dispatch_runnable_tasks SUCCESS")

        send_result_object_to_result_service(result_object=next_result_obj)
    else:

        logger.warning("SAME DISPATCH ID, running dispatch_runnable_tasks")

        dispatch_runnable_tasks(
            result_obj=result_obj, tasks_queue=tasks_queue, task_order=new_tasks_order
        )

        logger.warning("dispatch_runnable_tasks SUCCESS")
