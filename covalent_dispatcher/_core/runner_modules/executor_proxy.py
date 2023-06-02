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

""" Monitor executor instances """


from typing import Any

from covalent._shared_files import logger
from covalent.executor.base import _AbstractBaseExecutor as _ABE
from covalent.executor.utils import Signals

from .jobs import (
    get_cancel_requested,
    get_job_status,
    get_version_info,
    put_job_handle,
    put_job_status,
)

app_log = logger.app_log
log_stack_info = logger.log_stack_info

_putters = {}
_getters = {}


_putters["job_handle"] = put_job_handle
_putters["job_status"] = put_job_status
_getters["cancel_requested"] = get_cancel_requested
_getters["job_status"] = get_job_status
_getters["version_info"] = get_version_info


async def _handle_message(
    dispatch_id: str, task_id: int, executor: _ABE, action: Signals, body: Any = None
) -> Any:
    """
    Handle the action properly

    Arg(s)
        dispatch_id: Dispatch ID of the lattice
        task_id: ID of the task in the lattice
        executor: Instance of the abstract base executor
        action: Action requested to be performed
        body: Content of the action/request made

    Return(s)
        Response corresponding to the action requested
    """
    if action == Signals.GET:
        return await _getters[body](dispatch_id, task_id)

    if action == Signals.PUT:
        key, val = body
        await _putters[key](dispatch_id, task_id, val)
        return None
    else:
        raise KeyError(f"Unknown action {action}")


async def watch(dispatch_id: str, task_id: int, executor: _ABE) -> None:
    """
    Watch the send and receive queues of the executor

    Arg(s)
        dispatch_id: Dispatch ID of the lattice
        task_id: ID of the task within the lattice
        executor: Instance of the abstract base executor

    Return(s)
        None
    """
    send_queue = executor._send_queue
    recv_queue = executor._recv_queue

    while True:
        action, body = await send_queue.get()
        app_log.debug(f"Received message {action} from executor {dispatch_id}:{task_id}")

        if action == Signals.EXIT:
            app_log.debug(f"Stopping listener for executor {dispatch_id}:{task_id}")
            break

        try:
            resp = await _handle_message(dispatch_id, task_id, executor, action, body)
            recv_queue.put_nowait((True, resp))
        except Exception as ex:
            app_log.warning(f"Error handling message {action} from executor: {ex}")
            recv_queue.put_nowait((False, None))
            break
