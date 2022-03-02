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


from app.schemas.task import CancelResponse, NodeID, NodeIDList, TaskStatus
from fastapi import APIRouter

router = APIRouter()


@router.post("/run", status_code=202, response_model=str)
def run_task(*, dispatch_id: str, node_ids: NodeIDList) -> str:
    """
    API Endpoint (/api/task/run) to run tasks
    """

    return {"response": "execution of tasks started"}


@router.get("/status", status_code=200, response_model=TaskStatus)
def check_status(*, dispatch_id: str, node_id: NodeID) -> TaskStatus:
    """
    API Endpoint (/api/task/status) to check status of a task
    """

    return {"status": "running"}


@router.post("/cancel", status_code=200, response_model=CancelResponse)
def cancel_task(*, dispatch_id: str, node_id: NodeID) -> CancelResponse:
    """
    API Endpoint (/api/task/cancel) to cancel a task
    """

    return {"cancelled_dispatch_id": "some_dispatch_id"}
