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

"""Tests for the Covalent executor base module."""

import os
import tempfile
from functools import partial
from unittest.mock import AsyncMock, MagicMock

import pytest

from covalent import DepsCall, TransportableObject
from covalent._results_manager import Result
from covalent._shared_files.exceptions import TaskCancelledError, TaskRuntimeError
from covalent.executor import BaseExecutor
from covalent.executor.base import AsyncBaseExecutor
from covalent.executor.utils.enums import Signals
from covalent.executor.utils.wrappers import wrapper_fn


class MockExecutor(BaseExecutor):
    def run(self, function, args, kwargs, task_metadata):
        return function(*args, **kwargs)


class MockAsyncExecutor(AsyncBaseExecutor):
    async def run(self, function, args, kwargs, task_metadata):
        return function(*args, **kwargs)


def test_write_streams_to_file(mocker):
    """Test write log streams to file method in BaseExecutor via LocalExecutor."""

    me = MockExecutor()

    # Case 1 - Check that relative log files that are written to are constructed in the results directory that is explicitly passed as an argument.
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = "relative.log"
        me.write_streams_to_file(
            stream_strings=["relative"], filepaths=[tmp_file], dispatch_id="", results_dir=tmp_dir
        )
        assert "relative.log" in os.listdir(tmp_dir)

        with open(f"{tmp_dir}/relative.log") as f:
            lines = f.readlines()
        assert lines[0] == "relative"

    # Case 2 - Check that absolute log files that are written to are constructed in the results directory that is explicitly passed as an argument.
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = tempfile.NamedTemporaryFile()
        me.write_streams_to_file(
            stream_strings=["absolute"],
            filepaths=[tmp_file.name],
            dispatch_id="",
            results_dir=tmp_dir,
        )
        assert os.path.isfile(tmp_file.name)

        with open(tmp_file.name) as f:
            lines = f.readlines()
        assert lines[0] == "absolute"


def test_wrapper_fn():
    import tempfile
    from pathlib import Path

    f = tempfile.NamedTemporaryFile(delete=True)
    tmp_path_before = f.name
    f.close()
    f = tempfile.NamedTemporaryFile(delete=True)
    tmp_path_after = f.name
    f.close()

    def f(x, y):
        return x * x, y

    def before(path):
        with open(path, "w") as f:
            f.write("Hello")

    def after(path):
        with open(path, "w") as f:
            f.write("Bye")

    args = [TransportableObject.make_transportable(5)]
    kwargs = {"y": TransportableObject.make_transportable(2)}

    before_args = [tmp_path_before]
    after_args = [tmp_path_after]
    serialized_cb_args = TransportableObject.make_transportable(before_args)
    serialized_cb_kwargs = TransportableObject.make_transportable({})
    serialized_ca_args = TransportableObject.make_transportable(after_args)
    serialized_ca_kwargs = TransportableObject.make_transportable({})

    serialized_fn = TransportableObject.make_transportable(f)
    serialized_cb = TransportableObject(before)
    serialized_ca = TransportableObject(after)

    call_before = [(serialized_cb, serialized_cb_args, serialized_cb_kwargs, "")]
    call_after = [(serialized_ca, serialized_ca_args, serialized_ca_kwargs, "")]
    serialized_output = wrapper_fn(serialized_fn, call_before, call_after, *args, **kwargs)

    assert serialized_output.get_deserialized() == (25, 2)

    with open(tmp_path_before, "r") as f:
        assert f.read() == "Hello"

    with open(tmp_path_after, "r") as f:
        assert f.read() == "Bye"

    Path(tmp_path_before).unlink()
    Path(tmp_path_after).unlink()


def test_wrapper_fn_calldep_retval_injection():
    """Test injecting calldep return values into main task"""

    def f(x=0, y=0):
        return x + y

    def identity(y):
        return y

    serialized_fn = TransportableObject(f)
    calldep = DepsCall(identity, args=[5], retval_keyword="y")
    call_before = [calldep.apply()]
    args = []
    kwargs = {"x": TransportableObject(2)}

    output = wrapper_fn(serialized_fn, call_before, [], *args, **kwargs)

    assert output.get_deserialized() == 7


def test_wrapper_fn_calldep_non_unique_retval_keys_injection():
    """Test injecting calldep return values into main task"""

    def f(x=0, y=[]):
        return x + sum(y)

    def identity(y):
        return y

    serialized_fn = TransportableObject(f)
    calldep_one = DepsCall(identity, args=[1], retval_keyword="y")
    calldep_two = DepsCall(identity, args=[2], retval_keyword="y")
    call_before = [calldep_one.apply(), calldep_two.apply()]
    args = []
    kwargs = {"x": TransportableObject(3)}

    output = wrapper_fn(serialized_fn, call_before, [], *args, **kwargs)

    assert output.get_deserialized() == 6


def test_base_executor_subclassing():
    """Test that executors must implement run"""

    class BrokenMockExecutor(BaseExecutor):
        def __init__(self):
            super().__init__(self)

    try:
        me = BrokenMockExecutor()
    except TypeError:
        assert True


def test_base_executor_run(mocker):
    """Cover BaseExecutor.run() abstract method"""

    def f(x):
        return x

    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {}

    mocker.patch("covalent.executor.BaseExecutor.__abstractmethods__", set())
    be = BaseExecutor()
    try:
        be.run(function, args, kwargs, {})
        assert False
    except NotImplementedError:
        assert True


def test_base_executor_execute(mocker):
    """Test the execute method"""

    def f(x, y):
        return x + y

    me = MockExecutor()

    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)
    mock_notify = mocker.patch("covalent.executor.BaseExecutor._notify")

    result, stdout, stderr, exception_raised = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    assert result.get_deserialized() == 5
    mock_notify.assert_called_with(Signals.EXIT)


@pytest.mark.asyncio
async def test_async_base_executor_run(mocker):
    """Cover AsyncBaseExecutor.run() abstract method"""

    def f(x):
        return x

    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {}

    mocker.patch("covalent.executor.base.AsyncBaseExecutor.__abstractmethods__", set())
    be = AsyncBaseExecutor()
    try:
        await be.run(function, args, kwargs, {})
        assert False
    except NotImplementedError:
        assert True


@pytest.mark.asyncio
async def test_base_executor_private_execute(mocker):
    """Test that `BaseExecutor._execute()` correctly invokes the real execute method"""

    def f(x, y):
        return x, y

    me = MockExecutor()

    me.execute = MagicMock()

    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    await me._execute(
        function=function,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )
    me.execute.assert_called_with(
        function,
        args,
        kwargs,
        dispatch_id,
        results_dir,
        node_id,
    )


@pytest.mark.asyncio
async def test_async_base_executor_private_execute(mocker):
    """Test that `AsyncBaseExecutor._execute()` correctly invokes the real execute method"""

    def f(x, y):
        return x, y

    async_me = MockAsyncExecutor()

    async_me.execute = AsyncMock()

    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    await async_me._execute(
        function=function,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )
    async_me.execute.assert_awaited_with(
        function,
        args,
        kwargs,
        dispatch_id,
        results_dir,
        node_id,
    )


def test_base_executor_passes_task_metadata(mocker):
    def f(x, y):
        return x, y

    def fake_run(function, args, kwargs, task_metadata):
        return task_metadata

    me = MockExecutor()
    me.run = fake_run
    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)
    mock_notify = mocker.patch("covalent.executor.BaseExecutor._notify")

    metadata, stdout, stderr, exception_raised = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )
    task_metadata = {"dispatch_id": dispatch_id, "node_id": node_id, "results_dir": results_dir}
    assert metadata == task_metadata
    mock_notify.assert_called_with(Signals.EXIT)


def test_base_async_executor_passes_task_metadata(mocker):
    import asyncio

    def f(x, y):
        return x, y

    async def fake_run(function, args, kwargs, task_metadata):
        return task_metadata

    me = MockAsyncExecutor()
    me.run = fake_run
    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)
    mock_notify = mocker.patch("covalent.executor.base.AsyncBaseExecutor._notify")

    awaitable = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    metadata, stdout, stderr, exception_raised = asyncio.run(awaitable)
    task_metadata = {"dispatch_id": dispatch_id, "node_id": node_id, "results_dir": results_dir}
    assert metadata == task_metadata
    mock_notify.assert_called_with(Signals.EXIT)


def test_async_write_streams_to_file(mocker):
    """Test write log streams to file method in AsyncBaseExecutor via LocalExecutor."""

    import asyncio

    me = MockAsyncExecutor()

    # Case 1 - Check that relative log files that are written to are constructed in the results directory that is explicitly passed as an argument.
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = "relative.log"
        write_awaitable = me.write_streams_to_file(
            stream_strings=["relative"], filepaths=[tmp_file], dispatch_id="", results_dir=tmp_dir
        )
        asyncio.run(write_awaitable)
        assert "relative.log" in os.listdir(tmp_dir)

        with open(f"{tmp_dir}/relative.log") as f:
            lines = f.readlines()
        assert lines[0] == "relative"

    # Case 2 - Check that absolute log files that are written to are constructed in the results directory that is explicitly passed as an argument.
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = tempfile.NamedTemporaryFile()
        write_awaitable = me.write_streams_to_file(
            stream_strings=["absolute"],
            filepaths=[tmp_file.name],
            dispatch_id="",
            results_dir=tmp_dir,
        )
        asyncio.run(write_awaitable)

        assert os.path.isfile(tmp_file.name)

        with open(tmp_file.name) as f:
            lines = f.readlines()
        assert lines[0] == "absolute"


def test_executor_setup_teardown_method(mocker):
    me = MockExecutor()
    me.setup = MagicMock()
    me.teardown = MagicMock()

    def f(x, y):
        return x + y

    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    task_metadata = {
        "dispatch_id": dispatch_id,
        "node_id": node_id,
        "results_dir": results_dir,
    }

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)
    mock_notify = mocker.patch("covalent.executor.BaseExecutor._notify")

    result, stdout, stderr, exception_raised = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    assert result.get_deserialized() == 5
    me.setup.assert_called_once_with(task_metadata=task_metadata)
    me.teardown.assert_called_once_with(task_metadata=task_metadata)
    mock_notify.assert_called_with(Signals.EXIT)


def test_async_executor_setup_teardown(mocker):
    import asyncio

    def f(x, y):
        return x, y

    me = MockAsyncExecutor()
    me.setup = AsyncMock()
    me.run = AsyncMock()
    me.teardown = AsyncMock()
    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)
    mock_notify = mocker.patch("covalent.executor.base.AsyncBaseExecutor._notify")

    awaitable = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    asyncio.run(awaitable)
    task_metadata = {"dispatch_id": dispatch_id, "node_id": node_id, "results_dir": results_dir}
    me.run.assert_called_once_with(assembled_callable, args, kwargs, task_metadata)
    me.setup.assert_called_once_with(task_metadata=task_metadata)
    me.teardown.assert_called_once_with(task_metadata=task_metadata)
    mock_notify.assert_called_with(Signals.EXIT)


def test_executor_from_dict_makes_deepcopy():
    """Check that executor makes a deep copy of the provided metadata
    when rehydrating itself.
    """

    me = MockExecutor(log_stdout="/tmp/stdout.log")
    object_dict = me.to_dict()
    me = me.from_dict(object_dict)
    me._state = "runtime_state"
    assert "_state" not in object_dict["attributes"]


def test_executor_execute_runtime_error_handling(mocker):
    """Check handling of `TaskRuntimeError` exceptions"""

    def f(x, y):
        return x, y

    me = MockExecutor(log_stdout="/tmp/stdout.log")
    me.run = MagicMock(side_effect=TaskCancelledError("error"))

    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)
    mock_notify = mocker.patch("covalent.executor.BaseExecutor._notify")
    output, stdout, stderr, job_status = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    assert job_status is Result.CANCELLED
    mock_notify.assert_called_with(Signals.EXIT)


@pytest.mark.asyncio
async def test_async_base_executor_execute_runtime_error_handling(mocker):
    """Check handling of `TaskRuntimeError` exceptions"""

    def f(x, y):
        return x, y

    me = MockAsyncExecutor(log_stdout="/tmp/stdout.log")
    me.run = AsyncMock(side_effect=TaskCancelledError("error"))

    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)
    mock_notify = mocker.patch("covalent.executor.base.AsyncBaseExecutor._notify")

    output, stdout, stderr, job_status = await me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    assert job_status is Result.CANCELLED
    mock_notify.assert_called_with(Signals.EXIT)


def test_base_executor_get_cancel_requested(mocker):
    """
    Test executor invoking get cancel requested
    """
    me = MockExecutor()
    me._init_runtime()
    recv_queue = me._recv_queue
    recv_queue.put_nowait((True, True))
    mock_notify = mocker.patch("covalent.executor.base.BaseExecutor._notify")

    assert me.get_cancel_requested() is True
    mock_notify.assert_called_once()


def test_base_executor_get_version_info(mocker):
    """
    Test executor invoking get cancel requested
    """
    me = MockExecutor()
    me._init_runtime()
    recv_queue = me._recv_queue
    mock_version_info = {"python": "3.8", "covalent": "1.0"}
    recv_queue.put_nowait((True, mock_version_info))
    mock_notify = mocker.patch("covalent.executor.base.BaseExecutor._notify")

    assert me.get_version_info() == mock_version_info
    mock_notify.assert_called_once()


@pytest.mark.asyncio
async def test_async_base_executor_get_cancel_requested(mocker):
    me = MockAsyncExecutor()
    me._init_runtime()
    send_queue = me._send_queue
    recv_queue = me._recv_queue
    recv_queue.put_nowait((True, True))
    assert await me.get_cancel_requested() is True


@pytest.mark.asyncio
async def test_async_base_executor_get_version_info(mocker):
    me = MockAsyncExecutor()
    me._init_runtime()
    send_queue = me._send_queue
    recv_queue = me._recv_queue
    mock_version_info = {"python": "3.8", "covalent": "1.0"}
    recv_queue.put_nowait((True, mock_version_info))
    assert await me.get_version_info() == mock_version_info


def test_base_executor_set_job_handle(mocker):
    me = MockExecutor()
    me._init_runtime()
    send_queue = me._send_queue
    recv_queue = me._recv_queue
    recv_queue.put_nowait((True, None))

    mock_notify = mocker.patch("covalent.executor.base.BaseExecutor._notify")
    me.set_job_handle(42)

    mock_notify.assert_called_once()


@pytest.mark.asyncio
async def test_async_base_executor_set_job_handle(mocker):
    me = MockAsyncExecutor()
    me._init_runtime()
    send_queue = me._send_queue
    recv_queue = me._recv_queue

    mock_notify = mocker.patch("covalent.executor.base.AsyncBaseExecutor._notify")
    recv_queue.put_nowait((True, None))
    await me.set_job_handle(42)

    mock_notify.assert_called_once()


def test_base_executor_notify(mocker):
    me = MockExecutor()
    me._init_runtime(loop=MagicMock())
    me._loop.call_soon_threadsafe = MagicMock()

    me._notify("get")
    me._loop.call_soon_threadsafe.assert_called_with(me._send_queue.put_nowait, ("get", None))


def test_wait_for_response_runtimeerror(mocker):
    me = MockExecutor()
    me._init_runtime()
    me._recv_queue.get = MagicMock(return_value=(None, None))

    with pytest.raises(RuntimeError):
        me._wait_for_response()

    me._recv_queue.get.assert_called()


def test_base_executor_executor_task_runtime_error(mocker):
    """Check handling of `TaskRuntimeError` exceptions"""

    def f(x, y):
        return x, y

    me = MockExecutor(log_stdout="/tmp/stdout.log")
    me.run = MagicMock(side_effect=TaskRuntimeError("error"))

    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)
    mock_notify = mocker.patch("covalent.executor.BaseExecutor._notify")
    output, stdout, stderr, job_status = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    assert job_status is Result.FAILED
    mock_notify.assert_called_with(Signals.EXIT)


def test_base_executor_cancel_app_log(mocker):
    me = MockExecutor()
    me._init_runtime()
    mock_app_log = mocker.patch("covalent.executor.base.app_log.debug")
    task_metadata = {}
    job_handle = 42

    result = me.cancel(task_metadata, job_handle)
    mock_app_log.assert_called_once()
    assert result is False


@pytest.mark.asyncio
async def test_base_executor_cancel(mocker):
    me = MockExecutor()
    me._init_runtime(loop=AsyncMock(), cancel_pool=MagicMock())
    me._loop.run_in_executor = AsyncMock()
    await me._cancel({}, 42)
    me._loop.run_in_executor.assert_awaited()


@pytest.mark.asyncio
async def test_base_async_executor_wait_for_response_raises_runtimeerror(mocker):
    me = MockAsyncExecutor()
    me._init_runtime()
    me._recv_queue = AsyncMock()

    mock_async_wait_for = mocker.patch(
        "covalent.executor.base.asyncio.wait_for",
        return_value=(
            False,
            None,
        ),
    )

    with pytest.raises(RuntimeError):
        await me._wait_for_response()
        me._recv_queue.get.assert_called()
        mock_async_wait_for.assert_awaited()


@pytest.mark.asyncio
async def test_base_async_executor_task_runtime_error(mocker):
    me = MockAsyncExecutor()
    me._init_runtime()

    def f(x, y):
        return x, y

    me.setup = AsyncMock()
    me.teardown = AsyncMock()
    me._notify = MagicMock()
    me.run = AsyncMock(side_effect=TaskRuntimeError("error"))
    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1
    task_metadata = {"dispatch_id": dispatch_id, "node_id": node_id, "results_dir": results_dir}

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)
    output, stdout, stderr, job_status = await me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    me.setup.assert_awaited()
    me.run.assert_awaited_once_with(assembled_callable, args, kwargs, task_metadata)
    assert job_status is Result.FAILED
    me._notify.assert_called_with(Signals.EXIT)


@pytest.mark.asyncio
async def test_base_async_executor_task_cancel(mocker):
    mock_app_log = mocker.patch("covalent.executor.base.app_log.debug")
    me = MockAsyncExecutor()
    task_metadata = {}
    job_handle = 42
    result = await me.cancel(task_metadata=task_metadata, job_handle=job_handle)
    mock_app_log.assert_called_with(f"Cancel not implemented for executor {type(me)}")
    assert result is False


@pytest.mark.asyncio
async def test_base_async_executor_private_cancel(mocker):
    mock_app_log = mocker.patch("covalent.executor.base.app_log.debug")
    me = MockAsyncExecutor()
    me.teardown = AsyncMock()

    task_metadata = {}
    job_handle = 42

    cancel_result = await me._cancel(task_metadata=task_metadata, job_handle=job_handle)
    mock_app_log.assert_called_with(f"Cancel not implemented for executor {type(me)}")
    # me.teardown.assert_awaited_with(task_metadata)
    assert cancel_result is False
