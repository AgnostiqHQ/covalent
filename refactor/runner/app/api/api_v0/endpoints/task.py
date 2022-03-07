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


from typing import Dict

from app.schemas.task import CancelResponse, RunTaskResponse, TaskIds, TaskStatus
from fastapi import APIRouter

router = APIRouter()


@router.post("/{dispatch_id}/task", status_code=202, response_model=RunTaskResponse)
def run_task(*, dispatch_id: str, task_ids: TaskIds) -> RunTaskResponse:
    """
    API Endpoint (/workflow/task/run) to run tasks
    """

    return {"response": "execution of tasks started"}


@router.get("/{dispatch_id}/task/{task_id}", status_code=200, response_model=TaskStatus)
def check_status(*, dispatch_id: str, task_id: int) -> TaskStatus:
    """
    API Endpoint (/api/workflow/task/status) to check status of a task
    """

    return {"status": "running"}


@router.delete(
    "/{dispatch_id}/task/{task_id}/cancel", status_code=200, response_model=CancelResponse
)
def cancel_task(*, dispatch_id: str, task_id: int) -> CancelResponse:
    """
    API Endpoint (/api/workflow/task/cancel) to cancel a task
    """

    return {"cancelled_dispatch_id": f"{dispatch_id}", "cancelled_task_id": f"{task_id}"}
