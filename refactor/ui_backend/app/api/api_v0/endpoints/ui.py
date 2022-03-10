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
import asyncio
from aiolimiter import AsyncLimiter

from app.schemas.ui import UpdateUIResponse
from fastapi import APIRouter, Request, BackgroundTasks

limiter = AsyncLimiter(1, 10)

router = APIRouter()

async def notify_frontend(app, dispatch_id, task_id):
    async with limiter:
        await app.sio.emit("result-update",{
            "result": {
                "dispatch_id": dispatch_id,
                "task_id": task_id
            }
        })
    

@router.put("/workflow/{dispatch_id}/task/{task_id}", status_code=200, response_model=UpdateUIResponse)
async def update_ui(*, dispatch_id: str, task_id: int, request: Request, background_tasks: BackgroundTasks) -> UpdateUIResponse:
    
    """
    API Endpoint (/api/workflow/task) to update ui frontend
    """
    background_tasks.add_task(notify_frontend, request.app, dispatch_id, task_id)
    return {"response": "UI Updated"}
