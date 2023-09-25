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
import json
import os
import tempfile
from unittest.mock import AsyncMock

import pytest

import covalent as ct
from covalent._shared_files import TaskRuntimeError
from covalent._shared_files.exceptions import TaskCancelledError
from covalent._workflow.transportable_object import TransportableObject
from covalent.executor.executor_plugins.dask import (
    _EXECUTOR_PLUGIN_DEFAULTS,
    DaskExecutor,
    ResourceMap,
    TaskSpec,
    run_task_from_uris_alt,
)
from covalent.executor.utils.serialize import serialize_node_asset


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


def test_dask_send_poll_receive(mocker):
    """Test running a task using send + poll + receive."""
    from dask.distributed import LocalCluster

    from covalent.executor import DaskExecutor

    cluster = LocalCluster()
    dask_exec = DaskExecutor(cluster.scheduler_address)
    mock_get_cancel_requested = mocker.patch.object(
        dask_exec, "get_cancel_requested", AsyncMock(return_value=False)
    )
    mock_set_job_handle = mocker.patch.object(dask_exec, "set_job_handle", AsyncMock())

    def task(x, y):
        return x + y

    dispatch_id = "test_dask_send_receive"
    node_id = 0
    task_group_id = 0

    x = TransportableObject(1)
    y = TransportableObject(2)
    deps = {}
    call_before = []
    call_after = []

    ser_task = serialize_node_asset(TransportableObject(task), "function")
    ser_deps = serialize_node_asset(deps, "deps")
    ser_cb = serialize_node_asset(deps, "call_before")
    ser_ca = serialize_node_asset(deps, "call_after")
    ser_x = serialize_node_asset(x, "output")
    ser_y = serialize_node_asset(y, "output")

    node_0_file = tempfile.NamedTemporaryFile("wb")
    node_0_file.write(ser_task)
    node_0_file.flush()

    deps_file = tempfile.NamedTemporaryFile("wb")
    deps_file.write(ser_deps)
    deps_file.flush()

    cb_file = tempfile.NamedTemporaryFile("wb")
    cb_file.write(ser_cb)
    cb_file.flush()

    ca_file = tempfile.NamedTemporaryFile("wb")
    ca_file.write(ser_ca)
    ca_file.flush()

    node_1_file = tempfile.NamedTemporaryFile("wb")
    node_1_file.write(ser_x)
    node_1_file.flush()

    node_2_file = tempfile.NamedTemporaryFile("wb")
    node_2_file.write(ser_y)
    node_2_file.flush()

    task_spec = TaskSpec(
        function_id=0,
        args_ids=[1, 2],
        kwargs_ids={},
        deps_id="deps",
        call_before_id="call_before",
        call_after_id="call_after",
    )

    resources = ResourceMap(
        functions={
            0: node_0_file.name,
        },
        inputs={
            1: node_1_file.name,
            2: node_2_file.name,
        },
        deps={
            "deps": deps_file.name,
            "call_before": cb_file.name,
            "call_after": ca_file.name,
        },
    )

    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "node_ids": [node_id],
        "task_group_id": task_group_id,
    }

    async def run_dask_job(task_specs, resources, task_group_metadata):
        job_id = await dask_exec.send(task_specs, resources, task_group_metadata)
        job_status = await dask_exec.poll(task_group_metadata, job_id)
        task_updates = await dask_exec.receive(task_group_metadata, job_status)
        return job_status, task_updates

    job_status, task_updates = asyncio.run(
        run_dask_job([task_spec], resources, task_group_metadata)
    )

    assert job_status["status"] == "READY"
    assert len(task_updates) == 1
    task_update = task_updates[0]
    assert str(task_update.status) == (ct.status.COMPLETED)
    output_uri = task_update.assets["output"].remote_uri

    with open(output_uri, "rb") as f:
        output = TransportableObject.deserialize(f.read())
    assert output.get_deserialized() == 3


def test_run_task_from_uris_alt():
    """Test the wrapper submitted to dask"""

    def task(x, y):
        return x + y

    dispatch_id = "test_dask_send_receive"
    node_id = 0
    task_group_id = 0

    x = TransportableObject(1)
    y = TransportableObject(2)
    deps = {}

    cb_tmpfile = tempfile.NamedTemporaryFile()
    ca_tmpfile = tempfile.NamedTemporaryFile()

    call_before = [ct.DepsBash([f"echo Hello > {cb_tmpfile.name}"]).to_dict()]
    call_after = [ct.DepsBash(f"echo Bye > {ca_tmpfile.name}").to_dict()]

    ser_task = serialize_node_asset(TransportableObject(task), "function")
    ser_deps = serialize_node_asset(deps, "deps")
    ser_cb = serialize_node_asset(call_before, "call_before")
    ser_ca = serialize_node_asset(call_after, "call_after")
    ser_x = serialize_node_asset(x, "output")
    ser_y = serialize_node_asset(y, "output")

    node_0_file = tempfile.NamedTemporaryFile("wb")
    node_0_file.write(ser_task)
    node_0_file.flush()

    deps_file = tempfile.NamedTemporaryFile("wb")
    deps_file.write(ser_deps)
    deps_file.flush()

    cb_file = tempfile.NamedTemporaryFile("wb")
    cb_file.write(ser_cb)
    cb_file.flush()

    ca_file = tempfile.NamedTemporaryFile("wb")
    ca_file.write(ser_ca)
    ca_file.flush()

    node_1_file = tempfile.NamedTemporaryFile("wb")
    node_1_file.write(ser_x)
    node_1_file.flush()

    node_2_file = tempfile.NamedTemporaryFile("wb")
    node_2_file.write(ser_y)
    node_2_file.flush()

    task_spec = TaskSpec(
        function_id=0,
        args_ids=[1, 2],
        kwargs_ids={},
        deps_id="deps",
        call_before_id="call_before",
        call_after_id="call_after",
    )

    resources = ResourceMap(
        functions={
            0: node_0_file.name,
        },
        inputs={
            1: node_1_file.name,
            2: node_2_file.name,
        },
        deps={
            "deps": deps_file.name,
            "call_before": cb_file.name,
            "call_after": ca_file.name,
        },
    )

    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "node_ids": [node_id],
        "task_group_id": task_group_id,
    }

    result_file = tempfile.NamedTemporaryFile()
    stdout_file = tempfile.NamedTemporaryFile()
    stderr_file = tempfile.NamedTemporaryFile()

    results_dir = tempfile.TemporaryDirectory()

    run_task_from_uris_alt(
        task_specs=[task_spec.dict()],
        resources=resources.dict(),
        output_uris=[(result_file.name, stdout_file.name, stderr_file.name)],
        results_dir=results_dir.name,
        task_group_metadata=task_group_metadata,
        server_url="http://localhost:48008",
    )

    with open(result_file.name, "rb") as f:
        output = TransportableObject.deserialize(f.read())
    assert output.get_deserialized() == 3

    with open(cb_tmpfile.name, "r") as f:
        assert f.read() == "Hello\n"

    with open(ca_tmpfile.name, "r") as f:
        assert f.read() == "Bye\n"


def test_run_task_from_uris_alt_exception():
    """Test the wrapper submitted to dask"""

    def task(x, y):
        assert False

    dispatch_id = "test_dask_send_receive"
    node_id = 0
    task_group_id = 0

    x = TransportableObject(1)
    y = TransportableObject(2)
    deps = {}

    cb_tmpfile = tempfile.NamedTemporaryFile()
    ca_tmpfile = tempfile.NamedTemporaryFile()

    call_before = [ct.DepsBash([f"echo Hello > {cb_tmpfile.name}"]).to_dict()]
    call_after = [ct.DepsBash(f"echo Bye > {ca_tmpfile.name}").to_dict()]

    ser_task = serialize_node_asset(TransportableObject(task), "function")
    ser_deps = serialize_node_asset(deps, "deps")
    ser_cb = serialize_node_asset(call_before, "call_before")
    ser_ca = serialize_node_asset(call_after, "call_after")
    ser_x = serialize_node_asset(x, "output")
    ser_y = serialize_node_asset(y, "output")

    node_0_file = tempfile.NamedTemporaryFile("wb")
    node_0_file.write(ser_task)
    node_0_file.flush()

    deps_file = tempfile.NamedTemporaryFile("wb")
    deps_file.write(ser_deps)
    deps_file.flush()

    cb_file = tempfile.NamedTemporaryFile("wb")
    cb_file.write(ser_cb)
    cb_file.flush()

    ca_file = tempfile.NamedTemporaryFile("wb")
    ca_file.write(ser_ca)
    ca_file.flush()

    node_1_file = tempfile.NamedTemporaryFile("wb")
    node_1_file.write(ser_x)
    node_1_file.flush()

    node_2_file = tempfile.NamedTemporaryFile("wb")
    node_2_file.write(ser_y)
    node_2_file.flush()

    task_spec = TaskSpec(
        function_id=0,
        args_ids=[1],
        kwargs_ids={"y": 2},
        deps_id="deps",
        call_before_id="call_before",
        call_after_id="call_after",
    )

    resources = ResourceMap(
        functions={
            0: f"file://{node_0_file.name}",
        },
        inputs={
            1: f"file://{node_1_file.name}",
            2: f"file://{node_2_file.name}",
        },
        deps={
            "deps": f"file://{deps_file.name}",
            "call_before": f"file://{cb_file.name}",
            "call_after": f"file://{ca_file.name}",
        },
    )

    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "node_ids": [node_id],
        "task_group_id": task_group_id,
    }

    result_file = tempfile.NamedTemporaryFile()
    stdout_file = tempfile.NamedTemporaryFile()
    stderr_file = tempfile.NamedTemporaryFile()

    results_dir = tempfile.TemporaryDirectory()

    run_task_from_uris_alt(
        task_specs=[task_spec.dict()],
        resources=resources.dict(),
        output_uris=[(result_file.name, stdout_file.name, stderr_file.name)],
        results_dir=results_dir.name,
        task_group_metadata=task_group_metadata,
        server_url="http://localhost:48008",
    )
    summary_file_path = f"{results_dir.name}/result-{dispatch_id}:{node_id}.json"

    with open(summary_file_path, "r") as f:
        summary = json.load(f)
        assert summary["exception_occurred"] is True
