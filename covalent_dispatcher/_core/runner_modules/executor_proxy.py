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

""" Monitor executor instances."""


from typing import Any

from covalent._shared_files import logger
from covalent.executor.base import _AbstractBaseExecutor as _ABE
from covalent.executor.utils import Signals

from ..data_modules import job_manager

app_log = logger.app_log
log_stack_info = logger.log_stack_info

_putters = {}
_getters = {}


async def _get_cancel_requested(dispatch_id: str, task_id: int):
    """
    Query the database for the task's cancellation status

    Arg(s)
        dispatch_id: Dispatch ID of the lattice
        task_id: ID of the task within the lattice

    Return(s)
        Cancellation status of the task

    """
    # Don't hit the DB for post-processing task
    if task_id < 0:
        return False

    app_log.debug(f"Get _handle_requested for executor {dispatch_id}:{task_id}")
    job_records = await job_manager.get_jobs_metadata(dispatch_id, [task_id])
    app_log.debug(f"Job record: {job_records[0]}")
    return job_records[0]["cancel_requested"]


async def _put_job_handle(dispatch_id: str, task_id: int, job_handle: str) -> bool:
    """
    Store the job handle of the task returned by the backend in the database

    Arg(s)
        dispatch_id: Dispatch ID of the lattice
        task_id: ID of the task within the lattice
        job_handle: Unique identifier of the task returned by the execution backend

    Return(s)
        True
    """
    # Don't hit the DB for post-processing task
    if task_id < 0:
        return False
    app_log.debug(f"Put job_handle for executor {dispatch_id}:{task_id}")
    await job_manager.set_job_handle(dispatch_id, task_id, job_handle)
    return True


_putters["job_handle"] = _put_job_handle
_getters["cancel_requested"] = _get_cancel_requested


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
