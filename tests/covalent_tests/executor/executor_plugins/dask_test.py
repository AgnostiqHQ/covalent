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

"""Tests for Covalent dask executor."""

import asyncio
import os
import tempfile
from unittest.mock import AsyncMock

import pytest

import covalent as ct
from covalent._shared_files import TaskRuntimeError
from covalent._shared_files.exceptions import TaskCancelledError
from covalent.executor.executor_plugins.dask import _EXECUTOR_PLUGIN_DEFAULTS, DaskExecutor


def test_dask_executor_init(mocker):
    """Test dask executor constructor"""

    mocker.patch("covalent.executor.executor_plugins.dask.get_config", side_effect=KeyError())
    default_workdir_path = _EXECUTOR_PLUGIN_DEFAULTS["workdir"]

    de = DaskExecutor("127.0.0.1")

    assert de.scheduler_address == "127.0.0.1"
    assert de.workdir == default_workdir_path
    assert de.create_unique_workdir is False

    with tempfile.TemporaryDirectory() as tmp_dir:
        de = DaskExecutor("127.0.0.1", workdir=tmp_dir, create_unique_workdir=True)
        assert de.scheduler_address == "127.0.0.1"
        assert de.workdir == tmp_dir
        assert de.create_unique_workdir is True


def test_dask_executor_with_workdir(mocker):
    from dask.distributed import LocalCluster

    with tempfile.TemporaryDirectory() as tmp_dir:
        lc = LocalCluster()
        de = ct.executor.DaskExecutor(
            lc.scheduler_address, workdir=tmp_dir, create_unique_workdir=True
        )

        @ct.lattice
        @ct.electron(executor=de)
        def simple_task(x, y):
            with open("job.txt", "w") as w:
                w.write(str(x + y))
            return "Done!"

        mock_get_cancel_requested = mocker.patch.object(
            de, "get_cancel_requested", AsyncMock(return_value=False)
        )
        mock_set_job_handle = mocker.patch.object(de, "set_job_handle", AsyncMock())

        args = [1, 2]
        kwargs = {}
        task_metadata = {"dispatch_id": "asdf", "node_id": 1}
        result = asyncio.run(de.run(simple_task, args, kwargs, task_metadata))
        assert result == "Done!"

        target_dir = os.path.join(
            tmp_dir, task_metadata["dispatch_id"], f"node_{task_metadata['node_id']}"
        )

        assert os.listdir(target_dir) == ["job.txt"]
        assert open(os.path.join(target_dir, "job.txt")).read() == "3"

        mock_get_cancel_requested.assert_awaited()
        mock_set_job_handle.assert_awaited()


def test_dask_wrapper_fn(mocker):
    import sys

    from covalent.executor.executor_plugins.dask import dask_wrapper

    def f(x):
        print("Hello", file=sys.stdout)
        print("Bye", file=sys.stderr)
        return x

    args = [5]
    kwargs = {}

    output, stdout, stderr, tb = dask_wrapper(f, args, kwargs)
    assert output == 5
    assert stdout == "Hello\n"
    assert stderr == "Bye\n"
    assert tb == ""


def test_dask_wrapper_fn_exception_handling(mocker):
    import sys

    from covalent.executor.executor_plugins.dask import dask_wrapper

    def f(x):
        raise RuntimeError("error")

    args = [5]
    kwargs = {}
    error_msg = "task failed"
    mocker.patch("traceback.TracebackException.from_exception", return_value=error_msg)
    output, stdout, stderr, tb = dask_wrapper(f, args, kwargs)
    assert tb == error_msg
    assert output is None


def test_dask_executor_run(mocker):
    """Test run method for Dask executor"""

    import io
    import sys

    from dask.distributed import LocalCluster

    from covalent.executor import DaskExecutor

    cluster = LocalCluster()

    dask_exec = DaskExecutor(cluster.scheduler_address)
    mock_get_cancel_requested = mocker.patch.object(
        dask_exec, "get_cancel_requested", AsyncMock(return_value=False)
    )
    mock_set_job_handle = mocker.patch.object(dask_exec, "set_job_handle", AsyncMock())

    def f(x, y):
        print("Hello", file=sys.stdout)
        print("Bye", file=sys.stderr)
        return x, y

    args = [5]
    kwargs = {"y": 7}
    task_metadata = {"dispatch_id": "asdf", "node_id": 1}
    dask_exec._task_stdout = io.StringIO()
    dask_exec._task_stderr = io.StringIO()
    result = asyncio.run(dask_exec.run(f, args, kwargs, task_metadata))

    assert result == (5, 7)
    assert dask_exec.task_stdout.getvalue() == "Hello\n"
    assert dask_exec.task_stderr.getvalue() == "Bye\n"
    mock_get_cancel_requested.assert_awaited()
    mock_set_job_handle.assert_awaited()


def test_dask_executor_run_cancel_requested(mocker):
    """
    Test dask executor cancel request
    """
    import io
    import sys

    from dask.distributed import LocalCluster

    from covalent.executor import DaskExecutor

    cluster = LocalCluster()

    dask_exec = DaskExecutor(cluster.scheduler_address)
    mock_get_cancel_requested = mocker.patch.object(
        dask_exec, "get_cancel_requested", AsyncMock(side_effect=TaskCancelledError)
    )
    mock_set_job_handle = mocker.patch.object(dask_exec, "set_job_handle", AsyncMock())

    def f(x, y):
        print("Hello", file=sys.stdout)
        print("Bye", file=sys.stderr)
        return x, y

    args = [5]
    kwargs = {"y": 7}
    task_metadata = {"dispatch_id": "asdf", "node_id": 1}
    dask_exec._task_stdout = io.StringIO()
    dask_exec._task_stderr = io.StringIO()
    with pytest.raises(TaskCancelledError):
        asyncio.run(dask_exec.run(f, args, kwargs, task_metadata))
        mock_get_cancel_requested.assert_awaited()
        mock_set_job_handle.assert_awaited()


def test_dask_executor_run_exception_handling(mocker):
    """Test run method for Dask executor"""

    import io
    import sys

    from dask.distributed import LocalCluster

    from covalent.executor import DaskExecutor

    cluster = LocalCluster()

    dask_exec = DaskExecutor(cluster.scheduler_address)
    mock_get_cancel_requested = mocker.patch.object(
        dask_exec, "get_cancel_requested", AsyncMock(return_value=False)
    )
    mock_set_job_handle = mocker.patch.object(dask_exec, "set_job_handle", AsyncMock())
    dask_exec._task_stdout = io.StringIO()
    dask_exec._task_stderr = io.StringIO()

    def f(x, y):
        print("f output")
        raise RuntimeError("error")

    args = [5]
    kwargs = {"y": 7}
    task_metadata = {"dispatch_id": "asdf", "node_id": 1}
    with pytest.raises(TaskRuntimeError):
        asyncio.run(dask_exec.run(f, args, kwargs, task_metadata))

    dask_exec._task_stdout.getvalue() == "f output"
    assert "RuntimeError" in dask_exec._task_stderr.getvalue()
    mock_get_cancel_requested.assert_awaited()
    mock_set_job_handle.assert_awaited()


def test_dask_app_log_debug_when_cancel_requested(mocker):
    """
    Test logging when task cancellation is requested
    """
    from dask.distributed import LocalCluster

    from covalent.executor import DaskExecutor

    cluster = LocalCluster()

    mock_app_log = mocker.patch("covalent.executor.executor_plugins.dask.app_log.debug")

    dask_exec = DaskExecutor(cluster.scheduler_address)
    mock_get_cancel_requested = mocker.patch.object(
        dask_exec, "get_cancel_requested", AsyncMock(return_value=True)
    )

    def f(x, y):
        print("f output")
        raise RuntimeError("error")

    args = [5]
    kwargs = {"y": 7}
    task_metadata = {"dispatch_id": "asdf", "node_id": 1}
    try:
        asyncio.run(dask_exec.run(f, args, kwargs, task_metadata))
    except TaskCancelledError:
        pass
    finally:
        mock_get_cancel_requested.assert_awaited_once()
        mock_app_log.assert_called_once()


def test_dask_task_cancel(mocker):
    """
    Test dask task cancellation method
    """
    from dask.distributed import LocalCluster

    from covalent.executor import DaskExecutor

    cluster = LocalCluster()

    mock_app_log = mocker.patch("covalent.executor.executor_plugins.dask.app_log.debug")

    dask_exec = DaskExecutor(cluster.scheduler_address)

    task_metadata = {}
    job_handle = 42

    result = asyncio.run(dask_exec.cancel(task_metadata, job_handle))
    mock_app_log.assert_called_with(f"Cancelled future with key {job_handle}")
    assert result is True
