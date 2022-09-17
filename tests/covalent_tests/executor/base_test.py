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

"""Tests for the Covalent executor base module."""

import os
import tempfile
from functools import partial
from unittest.mock import AsyncMock, MagicMock

import pytest

from covalent import DepsCall, TransportableObject
from covalent.executor import BaseExecutor, wrapper_fn
from covalent.executor._runtime.utils import ExecutorCache
from covalent.executor.base import AsyncBaseExecutor


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
    me._initialize_runtime()

    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)

    me._initialize_task_data(dispatch_id, node_id)
    result, stdout, stderr = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    assert result.get_deserialized() == 5
    assert me._get_task_data(dispatch_id, node_id, "_status") == "COMPLETED"


@pytest.mark.asyncio
async def test_base_executor_execute_async(mocker):
    """Test the _execute_async coroutine"""

    def f(x, y):
        return x + y

    me = MockExecutor()
    me._initialize_runtime()

    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)

    me.execute = MagicMock(return_value=(1, "", ""))
    me._initialize_task_data = MagicMock()
    result, stdout, stderr = await me._execute_async(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    me._initialize_task_data.assert_called_once_with(dispatch_id, node_id)

    me.execute.assert_called_once_with(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )


@pytest.mark.asyncio
async def test_async_executor_execute_async(mocker):
    """Test the _execute_async coroutine"""

    def f(x, y):
        return x + y

    me = MockAsyncExecutor()
    me._initialize_runtime()

    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)

    me.execute = AsyncMock(return_value=(1, "", ""))
    me._initialize_task_data = MagicMock()
    result, stdout, stderr = await me._execute_async(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    me._initialize_task_data.assert_called_once_with(dispatch_id, node_id)

    me.execute.assert_awaited_with(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )


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


def test_base_executor_passes_task_metadata(mocker):
    def f(x, y):
        return x, y

    def fake_run(function, args, kwargs, task_metadata):
        return task_metadata

    me = MockExecutor()
    me._initialize_runtime()
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

    me._initialize_task_data(dispatch_id, node_id)
    metadata, stdout, stderr = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )
    task_metadata = {"dispatch_id": dispatch_id, "node_id": node_id, "results_dir": results_dir}
    assert metadata == task_metadata


def test_base_async_executor_passes_task_metadata(mocker):
    import asyncio

    def f(x, y):
        return x, y

    async def fake_run(function, args, kwargs, task_metadata):
        return task_metadata

    me = MockAsyncExecutor()
    me._initialize_runtime()
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

    me._initialize_task_data(dispatch_id, node_id)
    awaitable = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    metadata, stdout, stderr = asyncio.run(awaitable)
    task_metadata = {"dispatch_id": dispatch_id, "node_id": node_id, "results_dir": results_dir}
    assert metadata == task_metadata


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

    me = MockExecutor()
    me._initialize_runtime()
    me.setup = MagicMock(return_value=task_metadata)
    me.teardown = MagicMock(return_value=None)
    me._tasks_left = 2

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)

    me._initialize_task_data(dispatch_id, node_id)
    result, stdout, stderr = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    assert result.get_deserialized() == 5
    me.setup.assert_called_once_with(task_metadata=task_metadata)
    me.teardown.assert_not_called()
    assert me._tasks_left == 1

    me.setup = MagicMock(return_value=task_metadata)
    me.teardown = MagicMock(return_value=None)

    me._initialize_task_data(dispatch_id, node_id)
    result, stdout, stderr = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )
    me.teardown.assert_called_once_with(task_metadata)
    assert me._tasks_left == 0


@pytest.mark.asyncio
async def test_async_executor_setup_teardown(mocker):
    def f(x, y):
        return x, y

    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)
    task_metadata = {"dispatch_id": dispatch_id, "node_id": node_id, "results_dir": results_dir}

    me = MockAsyncExecutor()
    me._initialize_runtime()
    me.setup = AsyncMock(return_value=task_metadata)
    me.run = AsyncMock()
    me.teardown = AsyncMock()
    me._tasks_left = 2

    me._initialize_task_data(dispatch_id, node_id)
    awaitable = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    await awaitable
    me.run.assert_called_once_with(assembled_callable, args, kwargs, task_metadata)
    me.setup.assert_awaited_once_with(task_metadata=task_metadata)
    me.teardown.assert_not_awaited()
    assert me._tasks_left == 1

    me.setup = AsyncMock(return_value=task_metadata)
    me.teardown = AsyncMock()

    me._initialize_task_data(dispatch_id, node_id)
    awaitable = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )
    await awaitable

    me.teardown.assert_awaited_once_with(task_metadata)
    assert me._tasks_left == 0


def test_get_shared_instance():
    me = MockExecutor()
    shared_me = me.get_shared_instance()
    assert shared_me.shared is True


def test_is_shared_instance():
    me = MockExecutor()
    assert me.is_shared_instance() is False
    me.shared = True
    assert me.is_shared_instance() is True


def test_base_executor_run_exception(mocker):
    """Check base executor's handling of exceptions in run"""

    def f():
        raise RuntimeError

    class MockCleanup:
        def __init__(self):
            self.times_called = 0

        def __call__(self, task_metadata):
            self.times_called += 1

    me = MockExecutor()
    me._initialize_runtime()

    me.teardown = MockCleanup()

    function = TransportableObject(f)
    args = []
    kwargs = {}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = 1
    assembled_callable = partial(wrapper_fn, function, call_before, call_after)
    me._initialize_task_data(dispatch_id, node_id)

    # BaseExecutor
    try:
        me.execute(
            function=assembled_callable,
            args=args,
            kwargs=kwargs,
            dispatch_id=dispatch_id,
            results_dir="tmp",
            node_id=node_id,
        )
        assert False

    except RuntimeError as ex:
        assert me._tasks_left == 0
        me.teardown.times_called == 1
        assert me._get_task_data(dispatch_id, node_id, "_status") == "FAILED"


def test_base_executor_run_cancellation(mocker):
    """Check base executor's handling of task cancellation"""

    import types

    def f():
        raise RuntimeError

    class MockCleanup:
        def __init__(self):
            self.times_called = 0

        def __call__(self, task_metadata):
            self.times_called += 1

    me = MockExecutor()
    me._initialize_runtime()

    me.teardown = MockCleanup()

    function = TransportableObject(f)
    args = []
    kwargs = {}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = 1
    assembled_callable = partial(wrapper_fn, function, call_before, call_after)

    def mock_run(self, function, args, kwargs, task_metadata):
        self._set_task_status(dispatch_id, node_id, "CANCELLING")
        return 1

    def mock_cancelled_run(self, function, args, kwargs, task_metadata):
        self._set_task_status(dispatch_id, node_id, "CANCELLING")
        raise RuntimeError("Task Cancelled")

    me.run = types.MethodType(mock_run, me)

    me._initialize_task_data(dispatch_id, node_id)
    me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir="tmp",
        node_id=node_id,
    )
    assert me._get_task_status(dispatch_id, node_id) == "COMPLETED"

    me.run = types.MethodType(mock_cancelled_run, me)

    with pytest.raises(RuntimeError) as ex:
        me.execute(
            function=assembled_callable,
            args=args,
            kwargs=kwargs,
            dispatch_id=dispatch_id,
            results_dir="tmp",
            node_id=node_id,
        )
        assert me._get_task_status(dispatch_id, node_id) == "CANCELLED"


@pytest.mark.asyncio
async def test_async_base_executor_run_exception(mocker):
    """Check async base executor's handling of exceptions in run"""

    def f():
        raise RuntimeError

    class MockAsyncCleanup:
        def __init__(self):
            self.times_called = 0

        async def __call__(self, task_metadata):
            self.times_called += 1

    async_me = MockAsyncExecutor()
    async_me._initialize_runtime()

    async_me.teardown = MockAsyncCleanup()

    function = TransportableObject(f)
    args = []
    kwargs = {}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = 1
    assembled_callable = partial(wrapper_fn, function, call_before, call_after)
    async_me._initialize_task_data(dispatch_id, node_id)

    # BaseAsyncExecutor
    try:
        awaitable = async_me.execute(
            function=assembled_callable,
            args=args,
            kwargs=kwargs,
            dispatch_id=dispatch_id,
            results_dir="tmp",
            node_id=node_id,
        )
        await awaitable
        assert False

    except RuntimeError as ex:
        assert async_me._tasks_left == 0
        async_me.teardown.times_called == 1
        assert async_me._get_task_data(dispatch_id, node_id, "_status") == "FAILED"


@pytest.mark.asyncio
async def test_async_executor_run_cancellation(mocker):
    """Check async executor's handling of task cancellation"""

    import types

    def f():
        raise RuntimeError

    class MockAsyncCleanup:
        def __init__(self):
            self.times_called = 0

        async def __call__(self, task_metadata):
            self.times_called += 1

    me = MockAsyncExecutor()
    me._initialize_runtime()

    me.teardown = MockAsyncCleanup()

    function = TransportableObject(f)
    args = []
    kwargs = {}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = 1
    assembled_callable = partial(wrapper_fn, function, call_before, call_after)

    async def mock_run(self, function, args, kwargs, task_metadata):
        self._set_task_status(dispatch_id, node_id, "CANCELLING")
        return 1

    async def mock_cancelled_run(self, function, args, kwargs, task_metadata):
        self._set_task_status(dispatch_id, node_id, "CANCELLING")
        raise RuntimeError("Task Cancelled")

    me.run = types.MethodType(mock_run, me)
    me._initialize_task_data(dispatch_id, node_id)

    await me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir="tmp",
        node_id=node_id,
    )
    assert me._get_task_status(dispatch_id, node_id) == "COMPLETED"

    me.run = types.MethodType(mock_cancelled_run, me)

    with pytest.raises(RuntimeError) as ex:
        await me.execute(
            function=assembled_callable,
            args=args,
            kwargs=kwargs,
            dispatch_id=dispatch_id,
            results_dir="tmp",
            node_id=node_id,
        )
        assert me._get_task_status(dispatch_id, node_id) == "CANCELLED"


def test_executor_clone_sets_instance_id():
    """Check that `clone()` sets instance_id correctly"""

    me = MockExecutor()
    me_2 = me.clone()
    assert me_2.instance_id != me.instance_id
    assert me_2.shared == me.shared


@pytest.mark.asyncio
async def test_base_async_executor_execute(mocker):
    """Test the execute method"""

    def f(x, y):
        return x + y

    me = MockAsyncExecutor()
    me._initialize_runtime()
    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)

    me._initialize_task_data(dispatch_id, node_id)
    result, stdout, stderr = await me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    assert result.get_deserialized() == 5
    assert me._get_task_data(dispatch_id, node_id, "_status") == "COMPLETED"


def test_executor_from_dict_makes_deepcopy():
    """Check that executor makes a deep copy of the provided metadata
    when rehydrating itself.
    """

    me = MockExecutor(log_stdout="/tmp/stdout.log")
    object_dict = me.to_dict()
    me = me.from_dict(object_dict)
    me._new_attr = "unpicklable_object"
    assert "_new_attr" not in object_dict["attributes"]


def test_executor_task_count_helpers():
    """Test incrementing and decrementing task count"""
    me = MockExecutor(log_stdout="/tmp/stdout.log")
    me._initialize_runtime()
    me._increment_task_count()
    assert me._tasks_left == 2
    me._decrement_task_count()
    assert me._tasks_left == 1


@pytest.mark.asyncio
async def test_async_executor_task_count_helpers():
    """Test incrementing and decrementing task count"""
    me = MockAsyncExecutor(log_stdout="/tmp/stdout.log")
    me._initialize_runtime()
    me._increment_task_count()
    assert me._tasks_left == 2
    me._decrement_task_count()
    assert me._tasks_left == 1


def test_executor_initialize_runtime():
    """Test registering executor instance with executor cache"""
    me = MockExecutor(log_stdout="/tmp/stdout.log")
    me.shared = True
    cache = ExecutorCache()
    cache.id_instance_map[me.instance_id] = None
    cache.tasks_per_instance[me.instance_id] = 5
    me._initialize_runtime(cache)

    assert cache.id_instance_map[me.instance_id] == me
    assert me._tasks_left == 5


@pytest.mark.asyncio
async def test_async_executor_initialize_runtime():
    """Test registering async executor instance with executor cache"""
    me = MockAsyncExecutor(log_stdout="/tmp/stdout.log")
    me.shared = True
    cache = ExecutorCache()
    cache.id_instance_map[me.instance_id] = None
    cache.tasks_per_instance[me.instance_id] = 5
    me._initialize_runtime(cache)

    assert cache.id_instance_map[me.instance_id] == me
    assert me._tasks_left == 5


def test_executor_initialize_task_data():
    """Test initializing task data"""
    me = MockExecutor(log_stdout="/tmp/stdout.log")
    me._initialize_runtime()
    me._initialize_task_data("asdf", 1)
    assert me._state["tasks"]["asdf"][1] == {"_status": "RUNNING"}


def test_executor_get_set_task_data():
    """Test get task data"""
    me = MockExecutor(log_stdout="/tmp/stdout.log")
    me._initialize_runtime()
    me._initialize_task_data("asdf", 1)
    me._set_task_data("asdf", 1, "_status", "RUNNING")
    me._set_task_data("asdf", 1, "jobID", 42)
    assert me._get_task_data("asdf", 1, "_status") == "RUNNING"
    assert me._get_task_data("asdf", 1, "jobID") == 42


@pytest.mark.asyncio
async def test_async_executor_initialize_task_data():
    """Test initializing task data"""
    me = MockAsyncExecutor(log_stdout="/tmp/stdout.log")
    me._initialize_runtime()
    me._initialize_task_data("asdf", 1)
    assert me._state["tasks"]["asdf"][1] == {"_status": "RUNNING"}


@pytest.mark.asyncio
async def test_async_executor_get_set_task_data():
    """Test get task data"""
    me = MockAsyncExecutor(log_stdout="/tmp/stdout.log")
    me._initialize_runtime()
    me._initialize_task_data("asdf", 1)
    me._set_task_data("asdf", 1, "_status", "RUNNING")
    me._set_task_data("asdf", 1, "jobID", 42)
    assert me._get_task_data("asdf", 1, "_status") == "RUNNING"
    assert me._get_task_data("asdf", 1, "jobID") == 42


def test_executor_get_task_status():
    me = MockExecutor(log_stdout="/tmp/stdout.log")
    me._initialize_runtime()
    me._initialize_task_data("asdf", 1)
    me._set_task_status("asdf", 1, "CANCELLED")
    assert me._get_task_status("asdf", 1) == "CANCELLED"

    me = MockAsyncExecutor(log_stdout="/tmp/stdout.log")
    me._initialize_runtime()
    me._initialize_task_data("asdf", 1)
    me._set_task_status("asdf", 1, "CANCELLED")
    assert me._get_task_status("asdf", 1) == "CANCELLED"


def test_executor_cancel_task(mocker):
    me = MockExecutor(log_stdout="/tmp/stdout.log")
    mock_cancel = mocker.patch("covalent.executor.base.BaseExecutor.cancel")
    me._initialize_runtime()
    me._initialize_task_data("asdf", 1)
    me._initialize_task_data("asdf", 2)
    me._set_task_status("asdf", 2, "COMPLETED")
    me._cancel_task("asdf", 1)
    assert me._get_task_status("asdf", 1) == "CANCELLING"
    mock_cancel.assert_called_with("asdf", 1)

    mock_cancel = mocker.patch("covalent.executor.base.BaseExecutor.cancel")
    me._cancel_task("asdf", 2)
    mock_cancel.assert_not_called()
    assert me._get_task_status("asdf", 2) == "COMPLETED"


@pytest.mark.asyncio
async def test_async_executor_cancel_task(mocker):
    me = MockAsyncExecutor(log_stdout="/tmp/stdout.log")
    mock_cancel = mocker.patch("covalent.executor.base.AsyncBaseExecutor.cancel")
    me._initialize_runtime()
    me._initialize_task_data("asdf", 1)
    me._initialize_task_data("asdf", 2)
    me._set_task_status("asdf", 2, "COMPLETED")
    await me._cancel_task("asdf", 1)
    assert me._get_task_status("asdf", 1) == "CANCELLING"
    mock_cancel.assert_awaited_with("asdf", 1)

    mock_cancel = mocker.patch("covalent.executor.base.AsyncBaseExecutor.cancel")
    await me._cancel_task("asdf", 2)
    mock_cancel.assert_not_awaited()
    assert me._get_task_status("asdf", 2) == "COMPLETED"


@pytest.mark.asyncio
async def test_async_executor_finalize(mocker):
    me = MockAsyncExecutor(log_stdout="/tmp/stdout.log")
    mock_cancel = mocker.patch("covalent.executor.base.AsyncBaseExecutor.cancel")
    mock_teardown = mocker.patch("covalent.executor.base.AsyncBaseExecutor.teardown")
    me._initialize_runtime()
    me._initialize_task_data("asdf", 1)
    me._initialize_task_data("asdf", 2)
    await me._finalize()
    assert me._get_task_status("asdf", 1) == "CANCELLING"
    assert me._get_task_status("asdf", 2) == "CANCELLING"
    mock_teardown.assert_awaited_once()
