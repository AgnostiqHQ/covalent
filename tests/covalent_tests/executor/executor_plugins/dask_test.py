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

"""Tests for Covalent dask executor."""

import asyncio
from unittest.mock import AsyncMock

import pytest

from covalent._shared_files import TaskRuntimeError
from covalent._shared_files.exceptions import TaskCancelledError
from covalent.executor.executor_plugins.dask import DaskExecutor


def test_dask_executor_init(mocker):
    """Test dask executor constructor"""

    from covalent.executor import DaskExecutor

    de = DaskExecutor("127.0.0.1")

    assert de.scheduler_address == "127.0.0.1"


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
    import io
    import sys

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
