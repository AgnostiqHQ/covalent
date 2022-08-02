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

import io
import os
import tempfile
from contextlib import redirect_stdout
from functools import partial

from covalent import DepsCall, TransportableObject
from covalent.executor import BaseExecutor, wrapper_fn
from covalent.executor.base import BaseAsyncExecutor, _AbstractBaseExecutor


class MockExecutor(BaseExecutor):
    def run(self, function, args, kwargs, task_metadata):
        return function(*args, **kwargs)


class MockAsyncExecutor(BaseAsyncExecutor):
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


def test_execute_in_conda_env(mocker):
    """Test execute in conda enve method in Base Executor object."""

    me = MockExecutor()

    mocker.patch("covalent.executor.BaseExecutor.get_conda_path", return_value=False)
    conda_env_fail_mock = mocker.patch("covalent.executor.BaseExecutor._on_conda_env_fail")
    me.execute_in_conda_env(
        "function",
        "function_version",
        "args",
        "kwargs",
        "conda_env",
        "cache_dir",
        "node_id",
    )
    conda_env_fail_mock.assert_called_once_with("function", "args", "kwargs", "node_id")


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

    result, stdout, stderr = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    assert result.get_deserialized() == 5


def test_base_executor_execute_conda(mocker):
    """Test the execute method with a condaenv"""

    def f(x, y):
        return x + y

    me = MockExecutor(conda_env="testenv")
    function = TransportableObject(f)
    args = [TransportableObject(2)]
    kwargs = {"y": TransportableObject(3)}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = -1

    mock_conda_exec = mocker.patch(
        "covalent.executor.BaseExecutor.execute_in_conda_env", return_value=TransportableObject(5)
    )

    assembled_callable = partial(wrapper_fn, function, call_before, call_after)

    result, stdout, stderr = me.execute(
        function=assembled_callable,
        args=args,
        kwargs=kwargs,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
        node_id=node_id,
    )

    assert result.get_deserialized() == 5
    mock_conda_exec.assert_called_once()


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
    """Test write log streams to file method in BaseAsyncExecutor via LocalExecutor."""

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


def test_get_shared_instance():
    me = MockExecutor()
    shared_me = me.get_shared_instance()
    assert me.instance_id == 0
    assert shared_me.instance_id > 0


def test_is_shared_instance():
    me = MockExecutor()
    assert me.is_shared_instance() is False
    me.instance_id = 1
    assert me.is_shared_instance() is True


def test_base_executor_run_exception(mocker):
    """Check base executor's handling of exceptions in run"""
    import asyncio

    def f():
        raise RuntimeError

    class MockCleanup:
        def __init__(self):
            self.times_called = 0

        def __call__(self):
            self.times_called += 1

    class MockAsyncCleanup:
        def __init__(self):
            self.times_called = 0

        async def __call__(self):
            self.times_called += 1

    me = MockExecutor()
    async_me = MockAsyncExecutor()

    me.cleanup = MockCleanup()
    async_me.cleanup = MockAsyncCleanup()

    function = TransportableObject(f)
    args = []
    kwargs = {}
    call_before = []
    call_after = []
    dispatch_id = "asdf"
    results_dir = "/tmp"
    node_id = 1
    assembled_callable = partial(wrapper_fn, function, call_before, call_after)

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
        assert me.tasks_left == 0
        me.cleanup.times_called == 1

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
        asyncio.run(awaitable)
        assert False

    except RuntimeError as ex:
        assert async_me.tasks_left == 0
        async_me.cleanup.times_called == 1
