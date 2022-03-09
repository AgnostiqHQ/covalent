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

from typing import List

from covalent._results_manager import Result


def cancel_workflow(result_obj: Result):
    """Main cancel function. Called by the user via ct.cancel(dispatch_id)."""

    # TODO - We need to know which tasks are currently running so that we can ask Runner API
    #  to terminate those tasks
    tasks_to_cancel = get_running_tasks()

    # TODO - Call cancel tasks
    cancelled_task_ids = cancel_task(tasks_to_cancel, result_obj)

    # TODO - Update results object with cancelled tasks - Special attention needs to be taken to
    #  cancel

    pass


def cancel_task(result_obj: Result, task_id_batch: List[int]) -> List:
    """Returns a list of tasks that was cancelled before completion."""

    pass


def get_running_tasks():
    pass
