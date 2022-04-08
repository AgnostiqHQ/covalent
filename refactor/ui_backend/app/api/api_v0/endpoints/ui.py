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
import logging

from aiolimiter import AsyncLimiter
from app.schemas.ui import DrawRequest, UpdateUIResponse
from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.encoders import jsonable_encoder

dispatch_set = set()
limiter = AsyncLimiter(1, 2)

router = APIRouter()


async def notify_frontend(app, topic: str, payload):
    await app.sio.emit(topic, payload)


async def throttle_request_update_notify(app, dispatch_id, task_id):
    global dispatch_set
    if (dispatch_id, task_id) not in dispatch_set:
        dispatch_set.add((dispatch_id, task_id))
        async with limiter:
            dispatch_set.remove((dispatch_id, task_id))
            logging.debug(
                f"Emitting websocket event to update task {task_id} in workflow {dispatch_id}"
            )
            await notify_frontend(
                app, "result-update", {"result": {"dispatch_id": dispatch_id, "task_id": task_id}}
            )


@router.put(
    "/workflow/{dispatch_id}/task/{task_id}", status_code=200, response_model=UpdateUIResponse
)
async def update_ui(
    *, dispatch_id: str, task_id: int, request: Request, background_tasks: BackgroundTasks
) -> UpdateUIResponse:

    """
    API Endpoint (/api/workflow/task) to update ui frontend
    """

    # throttle notify frontend calls in background
    background_tasks.add_task(throttle_request_update_notify, request.app, dispatch_id, task_id)

    return {"response": "UI Updated"}


@router.post("/workflow/draft", status_code=200, response_model=UpdateUIResponse)
async def draw_draft(*, payload: DrawRequest, request: Request) -> UpdateUIResponse:
    """
    API Endpoint (/api/workflow/draft) to draw workflow draft
    """

    await notify_frontend(request.app, "draw-request", jsonable_encoder(payload))

    return {"response": "UI Workflow Draft Sent"}
