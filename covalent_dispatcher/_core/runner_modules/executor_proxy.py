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

"""Monitor of executor instances"""

from typing import Any

from covalent._shared_files import logger
from covalent.executor.base import _AbstractBaseExecutor as _ABE

from ..data_modules import job_manager

app_log = logger.app_log
log_stack_info = logger.log_stack_info

_putters = {}
_getters = {}


async def _get_cancel_requested(dispatch_id: str, task_id: int):
    app_log.debug(f"Get _handle_requested for executor {dispatch_id}:{task_id}")
    job_records = await job_manager.get_jobs_metadata(dispatch_id, [task_id])
    app_log.debug(f"Job record: {job_records[0]}")
    return job_records[0]["cancel_requested"]


async def _put_job_handle(dispatch_id: str, task_id: int, job_handle: str):
    app_log.debug(f"Put job_handle for executor {dispatch_id}:{task_id}")
    await job_manager.set_job_handle(dispatch_id, task_id, job_handle)
    return True


_putters["job_handle"] = _put_job_handle
_getters["cancel_requested"] = _get_cancel_requested


async def _handle_message(
    dispatch_id: str, task_id: int, executor: _ABE, action: str, body: Any = None
):
    if action == "get":
        return await _getters[body](dispatch_id, task_id)

    if action == "put":
        key, val = body
        await _putters[key](dispatch_id, task_id, val)
        return None
    else:
        raise KeyError(f"Unknown action {action}")


async def watch(dispatch_id: str, task_id: int, executor: _ABE):
    send_queue = executor._send_queue
    recv_queue = executor._recv_queue

    while True:
        action, body = await send_queue.get()
        app_log.debug(f"Received message {action} from executor {dispatch_id}:{task_id}")

        if action == "bye":
            app_log.debug(f"Stopping listener for executor {dispatch_id}:{task_id}")
            break

        try:
            resp = await _handle_message(dispatch_id, task_id, executor, action, body)
            recv_queue.put_nowait((True, resp))
        except Exception as ex:
            app_log.warning(f"Error handling message {action} from executor: {ex}")
            recv_queue.put_nowait((False, None))
            break
