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

"""Endpoints to update status of running tasks."""


from fastapi import APIRouter, Request

from covalent._shared_files import logger

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()


@router.put("/update/task/{dispatch_id}/{node_id}")
async def update_task_status(dispatch_id: str, node_id: int, request: Request):
    """Updates the status of a running task.

    The request JSON will be passed to the task executor plugin's
    `receive()` method together with `dispatch_id` and `node_id`.
    """

    from .._core import runner_ng

    task_metadata = {
        "dispatch_id": dispatch_id,
        "node_id": node_id,
    }
    try:
        detail = await request.json()
        f"Task {task_metadata} marked ready with detail {detail}"
        # detail = {"status": Status(status.value.upper())}
        await runner_ng.mark_task_ready(task_metadata, detail)
        # app_log.debug(f"Marked task {dispatch_id}:{node_id} with status {status}")
        return f"Task {task_metadata} marked ready with detail {detail}"
    except Exception as e:
        app_log.debug(f"Exception in update_task_status: {e}")
        raise
