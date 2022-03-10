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

"""Workflow cancel functionality."""

from typing import List

from covalent._results_manager import Result


def cancel_workflow(result_obj: Result, task_id_batch: List[int] = None):
    """Main cancel function. Called by the user via ct.cancel(dispatch_id)."""

    tasks = get_all_task_ids() if not task_id_batch else task_id_batch

    for task_id in tasks:
        cancel_task(result_obj.dispatch_id, task_id)


def cancel_task(dispatch_id: str, task_id_batch: List[int]) -> bool:
    """Returns a list of tasks that was cancelled before completion."""

    pass


def is_task_running(dispatch_id, task_id):
    """Runner API tells me if task has completed"""

    pass


def get_all_task_ids():
    # TODO - return all task and sublattice task ids

    pass
