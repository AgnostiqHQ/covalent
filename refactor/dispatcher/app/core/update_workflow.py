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
from typing import Dict

from covalent._results_manager import Result

from .utils import _post_process, are_tasks_running


def update_workflow_results(task_execution_results: Dict, result_obj: Result) -> Result:
    """Main update function. Called by the Runner API when there is an update for task
    execution status."""

    # Update the task results
    result_obj._update_node(**task_execution_results)

    if task_execution_results["status"] == Result.FAILED:
        result_obj._status = Result.FAILED

    elif task_execution_results["status"] == Result.CANCELLED:
        result_obj._status = Result.CANCELLED

    # If workflow is completed, post-process result
    elif not are_tasks_running(result_obj=result_obj):

        result_obj._result = _post_process(
            lattice=result_obj.lattice,
            task_outputs=result_obj.get_all_node_outputs(),
        )

        result_obj._status = Result.COMPLETED

    if result_obj.status != Result.RUNNING:
        result_obj._end_time = datetime.now(timezone.utc)

    # if task_execution_results["status"] == Result.COMPLETED:
    #     # To get the runnable tasks
    #     tasks, functions, input_args, input_kwargs, executors = get_runnable_tasks(
    #         result_obj=result_obj,
    #         tasks_queue=tasks_queue,
    #     )

    #     if tasks:
    #         unrun_tasks = run_tasks(
    #             results_dir=result_obj.results_dir,
    #             dispatch_id=result_obj.dispatch_id,
    #             task_id_batch=tasks,
    #             functions=functions,
    #             input_args=input_args,
    #             input_kwargs=input_kwargs,
    #             executors=executors,
    #         )

    #         task_order = [unrun_tasks] + tasks_queue.get() if unrun_tasks else tasks_queue.get()

    #     else:
    #         task_order = tasks_queue.get()

    return result_obj
