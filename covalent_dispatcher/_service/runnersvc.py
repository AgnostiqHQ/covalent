# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Endpoints to update status of running tasks."""


from fastapi import APIRouter, Request

from covalent._shared_files import logger

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()


@router.put("/dispatches/{dispatch_id}/electrons/{node_id}/job")
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
