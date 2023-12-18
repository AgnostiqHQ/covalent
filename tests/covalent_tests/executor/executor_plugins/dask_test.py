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
import io
import json
import os
import sys
import tempfile
from unittest.mock import AsyncMock

import pytest
from dask.distributed import LocalCluster

import covalent as ct
from covalent._shared_files import TaskRuntimeError
from covalent._shared_files.exceptions import TaskCancelledError
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._workflow.transportable_object import TransportableObject
from covalent.executor.executor_plugins.dask import (
    _EXECUTOR_PLUGIN_DEFAULTS,
    DaskExecutor,
    ResourceMap,
    TaskSpec,
    dask_wrapper,
    run_task_group_alt,
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

    cluster = LocalCluster()
    dask_exec = DaskExecutor()

    mock_get_config = mocker.patch(
        "covalent.executor.executor_plugins.dask.get_config",
        return_value=cluster.scheduler_address,
    )

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
    hooks = {
        "deps": deps,
        "call_before": call_before,
        "call_after": call_after,
    }

    ser_task = serialize_node_asset(TransportableObject(task), "function")
    ser_hooks = serialize_node_asset(deps, "hooks")
    ser_x = serialize_node_asset(x, "output")
    ser_y = serialize_node_asset(y, "output")

    node_0_file = tempfile.NamedTemporaryFile("wb")
    node_0_file.write(ser_task)
    node_0_file.flush()

    hooks_file = tempfile.NamedTemporaryFile("wb")
    hooks_file.write(ser_hooks)
    hooks_file.flush()

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
    )

    resources = ResourceMap(
        functions={
            0: node_0_file.name,
        },
        inputs={
            1: node_1_file.name,
            2: node_2_file.name,
        },
        hooks={
            0: hooks_file.name,
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

    mock_get_config.assert_called_once()

    assert job_status["status"] == "READY"
    assert len(task_updates) == 1
    task_update = task_updates[0]
    assert str(task_update.status) == (ct.status.COMPLETED)
    output_uri = task_update.assets["output"].remote_uri

    with open(output_uri, "rb") as f:
        output = TransportableObject.deserialize(f.read())
    assert output.get_deserialized() == 3

    assert task_update.assets["output"].size == os.path.getsize(output_uri)


def test_run_task_group_alt():
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

    hooks = {
        "deps": deps,
        "call_before": call_before,
        "call_after": call_after,
    }

    ser_task = serialize_node_asset(TransportableObject(task), "function")
    ser_hooks = serialize_node_asset(hooks, "hooks")
    ser_x = serialize_node_asset(x, "output")
    ser_y = serialize_node_asset(y, "output")

    node_0_file = tempfile.NamedTemporaryFile("wb")
    node_0_file.write(ser_task)
    node_0_file.flush()

    hooks_file = tempfile.NamedTemporaryFile("wb")
    hooks_file.write(ser_hooks)
    hooks_file.flush()

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
    )

    resources = ResourceMap(
        functions={
            0: node_0_file.name,
        },
        inputs={
            1: node_1_file.name,
            2: node_2_file.name,
        },
        hooks={
            0: hooks_file.name,
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
    qelectron_db_file = tempfile.NamedTemporaryFile()

    results_dir = tempfile.TemporaryDirectory()

    run_task_group_alt(
        task_specs=[task_spec.dict()],
        resources=resources.dict(),
        output_uris=[
            (result_file.name, stdout_file.name, stderr_file.name, qelectron_db_file.name)
        ],
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


def test_run_task_group_alt_exception():
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

    hooks = {
        "deps": deps,
        "call_before": call_before,
        "call_after": call_after,
    }

    ser_task = serialize_node_asset(TransportableObject(task), "function")
    ser_hooks = serialize_node_asset(hooks, "hooks")
    ser_x = serialize_node_asset(x, "output")
    ser_y = serialize_node_asset(y, "output")

    node_0_file = tempfile.NamedTemporaryFile("wb")
    node_0_file.write(ser_task)
    node_0_file.flush()

    hooks_file = tempfile.NamedTemporaryFile("wb")
    hooks_file.write(ser_hooks)
    hooks_file.flush()

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
    )

    resources = ResourceMap(
        functions={
            0: f"file://{node_0_file.name}",
        },
        inputs={
            1: f"file://{node_1_file.name}",
            2: f"file://{node_2_file.name}",
        },
        hooks={
            0: f"file://{hooks_file.name}",
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
    qelectron_db_file = tempfile.NamedTemporaryFile()

    results_dir = tempfile.TemporaryDirectory()

    run_task_group_alt(
        task_specs=[task_spec.model_dump()],
        resources=resources.model_dump(),
        output_uris=[
            (result_file.name, stdout_file.name, stderr_file.name, qelectron_db_file.name)
        ],
        results_dir=results_dir.name,
        task_group_metadata=task_group_metadata,
        server_url="http://localhost:48008",
    )
    summary_file_path = f"{results_dir.name}/result-{dispatch_id}:{node_id}.json"

    with open(summary_file_path, "r") as f:
        summary = json.load(f)
        assert summary["exception_occurred"] is True


def test_get_upload_uri():
    """
    Test the get_upload_uri method
    """

    dispatch_id = "test_dask_send_receive"
    node_id = 0
    task_group_id = 0

    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "node_ids": [node_id],
        "task_group_id": task_group_id,
    }

    object_key = "test_object_key"

    dask_exec = DaskExecutor()

    path_string = str(dask_exec.get_upload_uri(task_group_metadata, object_key))

    assert dispatch_id in path_string
    assert str(task_group_id) in path_string
    assert object_key in path_string


@pytest.mark.asyncio
async def test_dask_receive_cancelled_tasks():
    dispatch_id = "mock_dispatch"
    task_group_metadata = {"dispatch_id": dispatch_id, "node_ids": [0, 1], "task_group_id": 0}
    dask_exec = DaskExecutor()
    updates = await dask_exec.receive(task_group_metadata, None)
    for task_update in updates:
        assert task_update.status == RESULT_STATUS.CANCELLED

        for _, asset in task_update.assets.items():
            assert asset.remote_uri == ""
            assert asset.size == 0
