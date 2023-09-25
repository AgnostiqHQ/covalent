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

"""Tests for Covalent local executor."""

import io
import json
import os
import tempfile
from functools import partial
from unittest.mock import MagicMock

import pytest

import covalent as ct
from covalent._shared_files import TaskRuntimeError
from covalent._shared_files.exceptions import TaskCancelledError
from covalent._workflow.transport import TransportableObject
from covalent.executor.executor_plugins.local import (
    _EXECUTOR_PLUGIN_DEFAULTS,
    LocalExecutor,
    TaskSpec,
    run_task_from_uris,
)
from covalent.executor.utils.serialize import serialize_node_asset
from covalent.executor.utils.wrappers import wrapper_fn


def test_local_executor_init(mocker):
    """Test local executor constructor"""

    mocker.patch("covalent.executor.executor_plugins.local.get_config", side_effect=KeyError())
    default_workdir_path = _EXECUTOR_PLUGIN_DEFAULTS["workdir"]

    le = LocalExecutor()

    assert le.workdir == default_workdir_path
    assert le.create_unique_workdir is False

    with tempfile.TemporaryDirectory() as tmp_dir:
        le = LocalExecutor(workdir=tmp_dir, create_unique_workdir=True)
        assert le.workdir == tmp_dir
        assert le.create_unique_workdir is True


def test_local_executor_with_workdir(mocker):
    with tempfile.TemporaryDirectory() as tmp_dir:
        le = ct.executor.LocalExecutor(workdir=tmp_dir, create_unique_workdir=True)

        @ct.lattice
        @ct.electron(executor=le)
        def simple_task(x, y):
            with open("job.txt", "w") as w:
                w.write(str(x + y))
            return "Done!"

        mock_set_job_handle = mocker.patch.object(le, "set_job_handle", MagicMock(return_value=42))
        mock_get_cancel_requested = mocker.patch.object(
            le, "get_cancel_requested", MagicMock(return_value=False)
        )

        args = [1, 2]
        kwargs = {}
        task_metadata = {"dispatch_id": "asdf", "node_id": 1}
        assert le.run(simple_task, args, kwargs, task_metadata)

        target_dir = os.path.join(
            tmp_dir, task_metadata["dispatch_id"], f"node_{task_metadata['node_id']}"
        )

        assert os.listdir(target_dir) == ["job.txt"]
        assert open(os.path.join(target_dir, "job.txt")).read() == "3"

        mock_set_job_handle.assert_called_once()
        mock_get_cancel_requested.assert_called_once()


def test_local_executor_passes_results_dir(mocker):
    """Test that the local executor calls the stream writing function with the results directory specified."""
    with tempfile.TemporaryDirectory() as tmp_dir:

        @ct.electron
        def simple_task(x, y):
            print(x, y)
            return x, y

        mocked_function = mocker.patch(
            "covalent.executor.executor_plugins.local.LocalExecutor.write_streams_to_file"
        )
        le = LocalExecutor()
        mock_set_job_handle = mocker.patch.object(le, "set_job_handle", MagicMock(return_value=42))
        mock_get_cancel_requested = mocker.patch.object(
            le, "get_cancel_requested", MagicMock(return_value=False)
        )
        mock__notify = mocker.patch.object(le, "_notify", MagicMock())

        assembled_callable = partial(wrapper_fn, TransportableObject(simple_task), [], [])

        le.execute(
            function=assembled_callable,
            args=[],
            kwargs={"x": TransportableObject(1), "y": TransportableObject(2)},
            dispatch_id="-1",
            results_dir=tmp_dir,
            node_id=0,
        )
        mocked_function.assert_called_once()
        mock_set_job_handle.assert_called_once()
        mock_get_cancel_requested.assert_called_once()
        mock__notify.assert_called_once()


def test_local_executor_json_serialization():
    import json

    le = LocalExecutor(log_stdout="/dev/null")
    json_le = json.dumps(le.to_dict())
    le_new = LocalExecutor().from_dict(json.loads(json_le))
    assert le.__dict__ == le_new.__dict__


def test_wrapper_fn_calldep_retval_injection():
    """Test injecting calldep return values into main task"""

    def f(x=0, y=0):
        return x + y

    def identity(y):
        return y

    serialized_fn = TransportableObject(f)
    calldep = ct.DepsCall(identity, args=[5], retval_keyword="y")
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
    calldep_one = ct.DepsCall(identity, args=[1], retval_keyword="y")
    calldep_two = ct.DepsCall(identity, args=[2], retval_keyword="y")
    call_before = [calldep_one.apply(), calldep_two.apply()]
    args = []
    kwargs = {"x": TransportableObject(3)}

    output = wrapper_fn(serialized_fn, call_before, [], *args, **kwargs)

    assert output.get_deserialized() == 6


def local_executor_run__mock_task(x):
    return x**2


def test_local_executor_run(mocker):
    le = LocalExecutor()
    mock_set_job_handle = mocker.patch.object(le, "set_job_handle", MagicMock(return_value=42))
    mock_get_cancel_requested = mocker.patch.object(
        le, "get_cancel_requested", MagicMock(return_value=False)
    )

    args = [5]
    kwargs = {}
    task_metadata = {"dispatch_id": "asdf", "node_id": 1}
    assert le.run(local_executor_run__mock_task, args, kwargs, task_metadata) == 25
    mock_set_job_handle.assert_called_once()
    mock_get_cancel_requested.assert_called_once()


def local_executor_run_exception_handling__mock_task(x):
    print("f output")
    raise RuntimeError("error")


def test_local_executor_run_exception_handling(mocker):
    le = LocalExecutor()
    mock_set_job_handle = mocker.patch.object(le, "set_job_handle", MagicMock(return_value=42))
    mock_get_cancel_requested = mocker.patch.object(
        le, "get_cancel_requested", MagicMock(return_value=False)
    )
    le._task_stdout = io.StringIO()
    le._task_stderr = io.StringIO()
    args = [5]
    kwargs = {}
    task_metadata = {"dispatch_id": "asdf", "node_id": 1}
    with pytest.raises(TaskRuntimeError) as ex:
        le.run(local_executor_run_exception_handling__mock_task, args, kwargs, task_metadata)
    le._task_stdout.getvalue() == "f output"
    assert "RuntimeError" in le._task_stderr.getvalue()


def test_local_executor_get_cancel_requested(mocker):
    """
    Test task cancellation request using the local executor
    """
    le = LocalExecutor()
    args = [5]
    kwargs = {}
    task_metadata = {"dispatch_id": "asdf", "node_id": 1}
    le.set_job_handle = MagicMock()
    le.get_cancel_requested = MagicMock(return_value=True)
    mock_app_log = mocker.patch("covalent.executor.executor_plugins.local.app_log.debug")

    args = [5]
    kwargs = {}
    task_metadata = {"dispatch_id": "asdf", "node_id": 1}

    with pytest.raises(TaskCancelledError):
        le.run(local_executor_run__mock_task, args, kwargs, task_metadata)
        le.get_cancel_requested.assert_called_once()
        assert mock_app_log.call_count == 2


def test_run_task_from_uris(mocker):
    """Test the wrapper submitted to local"""

    def task(x, y):
        return x + y

    dispatch_id = "test_dask_send_receive"
    node_id = 0
    task_group_id = 0
    server_url = "http://localhost:48008"

    x = TransportableObject(1)
    y = TransportableObject(2)
    deps = {}

    cb_tmpfile = tempfile.NamedTemporaryFile()
    ca_tmpfile = tempfile.NamedTemporaryFile()

    deps = {
        "bash": ct.DepsBash([f"echo Hello > {cb_tmpfile.name}"]).to_dict(),
        "pip": ct.DepsBash(f"echo Bye > {ca_tmpfile.name}").to_dict(),
    }

    call_before = []
    call_after = []

    ser_task = serialize_node_asset(TransportableObject(task), "function")
    ser_deps = serialize_node_asset(deps, "deps")
    ser_cb = serialize_node_asset(call_before, "call_before")
    ser_ca = serialize_node_asset(call_after, "call_after")
    ser_x = serialize_node_asset(x, "output")
    ser_y = serialize_node_asset(y, "output")

    node_0_file = tempfile.NamedTemporaryFile("wb")
    node_0_file.write(ser_task)
    node_0_file.flush()
    node_0_function_url = (
        f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/0/assets/function"
    )

    deps_file = tempfile.NamedTemporaryFile("wb")
    deps_file.write(ser_deps)
    deps_file.flush()
    deps_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/0/assets/deps"

    cb_file = tempfile.NamedTemporaryFile("wb")
    cb_file.write(ser_cb)
    cb_file.flush()
    cb_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/0/assets/call_before"

    ca_file = tempfile.NamedTemporaryFile("wb")
    ca_file.write(ser_ca)
    ca_file.flush()
    ca_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/0/assets/call_after"

    node_1_file = tempfile.NamedTemporaryFile("wb")
    node_1_file.write(ser_x)
    node_1_file.flush()
    node_1_output_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/1/assets/output"

    node_2_file = tempfile.NamedTemporaryFile("wb")
    node_2_file.write(ser_y)
    node_2_file.flush()
    node_2_output_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/2/assets/output"

    task_spec = TaskSpec(
        function_id=0,
        args_ids=[1, 2],
        kwargs_ids={},
        deps_id="deps",
        call_before_id="call_before",
        call_after_id="call_after",
    )

    resources = {
        node_0_function_url: ser_task,
        node_1_output_url: ser_x,
        node_2_output_url: ser_y,
        deps_url: ser_deps,
        cb_url: ser_cb,
        ca_url: ser_ca,
    }

    def mock_req_get(url, stream):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = resources[url]
        return mock_resp

    def mock_req_post(url, files):
        resources[url] = files["asset_file"].read()

    mocker.patch("requests.get", mock_req_get)
    mocker.patch("requests.post", mock_req_post)
    mock_put = mocker.patch("requests.put")
    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "node_ids": [node_id],
        "task_group_id": task_group_id,
    }

    result_file = tempfile.NamedTemporaryFile()
    stdout_file = tempfile.NamedTemporaryFile()
    stderr_file = tempfile.NamedTemporaryFile()

    results_dir = tempfile.TemporaryDirectory()

    run_task_from_uris(
        task_specs=[task_spec.dict()],
        resources={},
        output_uris=[(result_file.name, stdout_file.name, stderr_file.name)],
        results_dir=results_dir.name,
        task_group_metadata=task_group_metadata,
        server_url=server_url,
    )

    with open(result_file.name, "rb") as f:
        output = TransportableObject.deserialize(f.read())
    assert output.get_deserialized() == 3

    with open(cb_tmpfile.name, "r") as f:
        assert f.read() == "Hello\n"

    with open(ca_tmpfile.name, "r") as f:
        assert f.read() == "Bye\n"

    mock_put.assert_called()


def test_run_task_from_uris_exception(mocker):
    """Test the wrapper submitted to local"""

    def task(x, y):
        assert False

    dispatch_id = "test_dask_send_receive"
    node_id = 0
    task_group_id = 0
    server_url = "http://localhost:48008"

    x = TransportableObject(1)
    y = TransportableObject(2)
    deps = {}

    cb_tmpfile = tempfile.NamedTemporaryFile()
    ca_tmpfile = tempfile.NamedTemporaryFile()

    deps = {
        "bash": ct.DepsBash([f"echo Hello > {cb_tmpfile.name}"]).to_dict(),
        "pip": ct.DepsBash(f"echo Bye > {ca_tmpfile.name}").to_dict(),
    }

    call_before = []
    call_after = []

    ser_task = serialize_node_asset(TransportableObject(task), "function")
    ser_deps = serialize_node_asset(deps, "deps")
    ser_cb = serialize_node_asset(call_before, "call_before")
    ser_ca = serialize_node_asset(call_after, "call_after")
    ser_x = serialize_node_asset(x, "output")
    ser_y = serialize_node_asset(y, "output")

    node_0_file = tempfile.NamedTemporaryFile("wb")
    node_0_file.write(ser_task)
    node_0_file.flush()
    node_0_function_url = (
        f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/0/assets/function"
    )

    deps_file = tempfile.NamedTemporaryFile("wb")
    deps_file.write(ser_deps)
    deps_file.flush()
    deps_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/0/assets/deps"

    cb_file = tempfile.NamedTemporaryFile("wb")
    cb_file.write(ser_cb)
    cb_file.flush()
    cb_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/0/assets/call_before"

    ca_file = tempfile.NamedTemporaryFile("wb")
    ca_file.write(ser_ca)
    ca_file.flush()
    ca_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/0/assets/call_after"

    node_1_file = tempfile.NamedTemporaryFile("wb")
    node_1_file.write(ser_x)
    node_1_file.flush()
    node_1_output_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/1/assets/output"

    node_2_file = tempfile.NamedTemporaryFile("wb")
    node_2_file.write(ser_y)
    node_2_file.flush()
    node_2_output_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/2/assets/output"

    task_spec = TaskSpec(
        function_id=0,
        args_ids=[1],
        kwargs_ids={"y": 2},
        deps_id="deps",
        call_before_id="call_before",
        call_after_id="call_after",
    )

    resources = {
        node_0_function_url: ser_task,
        node_1_output_url: ser_x,
        node_2_output_url: ser_y,
        deps_url: ser_deps,
        cb_url: ser_cb,
        ca_url: ser_ca,
    }

    def mock_req_get(url, stream):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = resources[url]
        return mock_resp

    def mock_req_post(url, files):
        resources[url] = files["asset_file"].read()

    mocker.patch("requests.get", mock_req_get)
    mocker.patch("requests.post", mock_req_post)
    mocker.patch("requests.put")
    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "node_ids": [node_id],
        "task_group_id": task_group_id,
    }

    result_file = tempfile.NamedTemporaryFile()
    stdout_file = tempfile.NamedTemporaryFile()
    stderr_file = tempfile.NamedTemporaryFile()

    results_dir = tempfile.TemporaryDirectory()

    run_task_from_uris(
        task_specs=[task_spec.dict()],
        resources={},
        output_uris=[(result_file.name, stdout_file.name, stderr_file.name)],
        results_dir=results_dir.name,
        task_group_metadata=task_group_metadata,
        server_url=server_url,
    )

    summary_file_path = f"{results_dir.name}/result-{dispatch_id}:{node_id}.json"

    with open(summary_file_path, "r") as f:
        summary = json.load(f)
        assert summary["exception_occurred"] is True
