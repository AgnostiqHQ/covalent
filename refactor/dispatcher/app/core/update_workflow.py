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

from .dispatch_workflow import (
    dispatch_runnable_tasks,
    get_result_object_from_result_service,
    get_runnable_tasks,
    is_empty,
    run_tasks,
    send_result_object_to_result_service,
)
from .utils import _post_process, are_tasks_running


def update_workflow_results(
    task_execution_results: Dict, dispatch_id: str, tasks_queue: MPQ
) -> Result:
    """Main update function. Called by the Runner API when there is an update for task
    execution status."""

    # TODO: Place it in somewhere where only this result object needs to get updated
    latest_result_obj = get_result_object_from_result_service(dispatch_id=dispatch_id)

    # Update the task results
    latest_result_obj._update_node(**task_execution_results)

    if task_execution_results["status"] == Result.FAILED:
        latest_result_obj._status = Result.FAILED

    elif task_execution_results["status"] == Result.CANCELLED:
        latest_result_obj._status = Result.CANCELLED

    # If workflow is completed, post-process result
    elif not are_tasks_running(result_obj=latest_result_obj):

        latest_result_obj._result = _post_process(
            lattice=latest_result_obj.lattice,
            task_outputs=latest_result_obj.get_all_node_outputs(),
        )

        latest_result_obj._status = Result.COMPLETED

    elif task_execution_results["status"] == Result.COMPLETED and not is_empty(tasks_queue):

        tasks_order_lod = tasks_queue.get()

        tasks_dict = tasks_order_lod.pop(0)
        new_dispatch_id, new_tasks_order = tasks_dict.items()

        if tasks_order_lod:
            tasks_queue.put(tasks_order_lod)
        else:
            # Mark queue as empty
            tasks_queue.put(None)

        if new_dispatch_id != dispatch_id:
            next_result_obj = get_result_object_from_result_service(dispatch_id=new_dispatch_id)
            dispatch_runnable_tasks(
                result_obj=next_result_obj, tasks_queue=tasks_queue, task_order=new_tasks_order
            )
            send_result_object_to_result_service(result_object=next_result_obj)
        else:
            dispatch_runnable_tasks(
                result_obj=latest_result_obj, tasks_queue=tasks_queue, task_order=new_tasks_order
            )

    if latest_result_obj.status != Result.RUNNING:
        latest_result_obj._end_time = datetime.now(timezone.utc)

    return latest_result_obj
