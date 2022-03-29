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

    if latest_result_obj.status != Result.RUNNING:
        latest_result_obj._end_time = datetime.now(timezone.utc)

    if task_execution_results["status"] == Result.COMPLETED:

        # TODO: This logic might need change
        dispatch_runnable_tasks(latest_result_obj, tasks_queue)

    return latest_result_obj
