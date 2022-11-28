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

"""
Tests for the executor monitor
"""

import asyncio

import pytest

from covalent.executor.base import AsyncBaseExecutor, BaseExecutor
from covalent_dispatcher._core.runner_modules.executor_monitor import watch


class MockExecutor(BaseExecutor):
    def run(self, function, args, kwargs, task_metadata):
        return function(*args, **kwargs)


class MockAsyncExecutor(AsyncBaseExecutor):
    async def run(self, function, args, kwargs, task_metadata):
        return function(*args, **kwargs)


def get_mock_executor():
    me = MockExecutor()
    me._init_runtime()
    return me


def get_mock_async_executor():
    me = MockAsyncExecutor()
    me._init_runtime()
    return me


@pytest.mark.asyncio
async def test_watch_bye(mocker):
    me = get_mock_executor()
    send_queue = me._send_queue
    recv_queue = me._recv_queue
    send_queue.put_nowait(("bye", None))
    await asyncio.wait_for(watch("asdf", 0, me), 2)

    me = get_mock_async_executor()
    send_queue = me._send_queue
    recv_queue = me._recv_queue
    send_queue.put_nowait(("bye", None))
    await asyncio.wait_for(watch("asdf", 0, me), 2)


@pytest.mark.asyncio
async def test_watch_get(mocker):
    me = get_mock_executor()
    send_queue = me._send_queue
    recv_queue = me._recv_queue
    job_record = {"job_id": 1, "cancel_requested": True}
    dispatch_id = "dispatch"
    task_id = 0
    mock_get = mocker.patch(
        "covalent_dispatcher._core.runner_modules.executor_monitor.job_manager.get_job_metadata",
        return_value=job_record,
    )
    send_queue.put_nowait(("get", "cancel_requested"))
    send_queue.put_nowait(("bye", None))

    await asyncio.wait_for(watch(dispatch_id, task_id, me), 2)
    assert recv_queue.get_nowait() == (True, True)
    mock_get.assert_called_with(dispatch_id, task_id)

    me = get_mock_async_executor()
    send_queue = me._send_queue
    recv_queue = me._recv_queue
    send_queue.put_nowait(("get", "cancel_requested"))
    send_queue.put_nowait(("bye", None))

    await asyncio.wait_for(watch(dispatch_id, task_id, me), 2)
    assert recv_queue.get_nowait() == (True, True)
    mock_get.assert_called_with(dispatch_id, task_id)


@pytest.mark.asyncio
async def test_watch_put(mocker):
    import json

    me = get_mock_executor()
    send_queue = me._send_queue
    recv_queue = me._recv_queue

    dispatch_id = "dispatch"
    task_id = 0
    mock_set = mocker.patch(
        "covalent_dispatcher._core.runner_modules.executor_monitor.job_manager.set_job_handle",
    )
    job_handle = 42
    send_queue.put_nowait(("put", ("job_handle", json.dumps(job_handle))))
    send_queue.put_nowait(("bye", None))

    await asyncio.wait_for(watch(dispatch_id, task_id, me), 2)
    assert recv_queue.get_nowait() == (True, None)
    mock_set.assert_called_with(dispatch_id, task_id, json.dumps(job_handle))

    me = get_mock_async_executor()
    send_queue = me._send_queue
    recv_queue = me._recv_queue
    send_queue.put_nowait(("put", ("job_handle", json.dumps(job_handle))))
    send_queue.put_nowait(("bye", None))

    await asyncio.wait_for(watch(dispatch_id, task_id, me), 2)
    assert recv_queue.get_nowait() == (True, None)
    mock_set.assert_called_with(dispatch_id, task_id, json.dumps(job_handle))


@pytest.mark.asyncio
async def test_watch_error(mocker):
    import json

    me = get_mock_executor()
    send_queue = me._send_queue
    recv_queue = me._recv_queue

    dispatch_id = "dispatch"
    task_id = 0
    mock_set = mocker.patch(
        "covalent_dispatcher._core.runner_modules.executor_monitor.job_manager.set_job_handle",
    )
    job_handle = 42
    send_queue.put_nowait(("unknown_action", ("job_handle", json.dumps(job_handle))))
    send_queue.put_nowait(("bye", None))

    await asyncio.wait_for(watch(dispatch_id, task_id, me), 2)
    assert recv_queue.get_nowait() == (False, None)

    me = get_mock_async_executor()
    send_queue = me._send_queue
    recv_queue = me._recv_queue
    send_queue.put_nowait(("unknown_action", ("job_handle", json.dumps(job_handle))))
    send_queue.put_nowait(("bye", None))

    await asyncio.wait_for(watch(dispatch_id, task_id, me), 2)
    assert recv_queue.get_nowait() == (False, None)
