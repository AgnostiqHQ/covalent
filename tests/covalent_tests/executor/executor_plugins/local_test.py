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

"""Tests for Covalent local executor."""

import io
import json
import os
import tempfile
from functools import partial
from unittest.mock import MagicMock, Mock, patch

import pytest

import covalent as ct
from covalent._shared_files import TaskRuntimeError
from covalent._shared_files.exceptions import TaskCancelledError
from covalent._workflow.transport import TransportableObject
from covalent.executor.executor_plugins.local import (
    _EXECUTOR_PLUGIN_DEFAULTS,
    RESULT_STATUS,
    LocalExecutor,
    StatusEnum,
    TaskSpec,
    run_task_group,
)
from covalent.executor.schemas import ResourceMap
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


def test_run_task_group(mocker):
    """Test the wrapper submitted to local"""

    def task(x, y):
        return x + y

    dispatch_id = "test_local_send_receive"
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
    node_0_function_url = (
        f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/0/assets/function"
    )

    hooks_file = tempfile.NamedTemporaryFile("wb")
    hooks_file.write(ser_hooks)
    hooks_file.flush()
    hooks_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/0/assets/hooks"

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
    )

    resources = {
        node_0_function_url: ser_task,
        node_1_output_url: ser_x,
        node_2_output_url: ser_y,
        hooks_url: ser_hooks,
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
    qelectron_db_file = tempfile.NamedTemporaryFile()

    results_dir = tempfile.TemporaryDirectory()

    run_task_group(
        task_specs=[task_spec.dict()],
        output_uris=[
            (result_file.name, stdout_file.name, stderr_file.name, qelectron_db_file.name)
        ],
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


def test_run_task_group_exception(mocker):
    """Test the wrapper submitted to local"""

    def task(x, y):
        assert False

    dispatch_id = "test_local_send_receive"
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
    node_0_function_url = (
        f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/0/assets/function"
    )

    hooks_file = tempfile.NamedTemporaryFile("wb")
    hooks_file.write(ser_hooks)
    hooks_file.flush()
    hooks_url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/0/assets/hooks"

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
    )

    resources = {
        node_0_function_url: ser_task,
        node_1_output_url: ser_x,
        node_2_output_url: ser_y,
        hooks_url: ser_hooks,
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
    qelectron_db_file = tempfile.NamedTemporaryFile()

    results_dir = tempfile.TemporaryDirectory()

    run_task_group(
        task_specs=[task_spec.dict()],
        output_uris=[
            (result_file.name, stdout_file.name, stderr_file.name, qelectron_db_file.name)
        ],
        results_dir=results_dir.name,
        task_group_metadata=task_group_metadata,
        server_url=server_url,
    )

    summary_file_path = f"{results_dir.name}/result-{dispatch_id}:{node_id}.json"

    with open(summary_file_path, "r") as f:
        summary = json.load(f)
        assert summary["exception_occurred"] is True


# Mocks for external dependencies
@pytest.fixture
def mock_os_path_join():
    with patch("os.path.join", return_value="mock_path") as mock:
        yield mock


@pytest.fixture
def mock_format_server_url():
    with patch(
        "covalent.executor.executor_plugins.local.format_server_url",
        return_value="mock_server_url",
    ) as mock:
        yield mock


@pytest.fixture
def mock_future():
    mock = Mock()
    mock.cancelled.return_value = False
    return mock


@pytest.fixture
def mock_proc_pool_submit(mock_future):
    with patch(
        "covalent.executor.executor_plugins.local.proc_pool.submit", return_value=mock_future
    ) as mock:
        yield mock


# Test cases
test_cases = [
    # Happy path
    {
        "id": "happy_path",
        "task_specs": [
            TaskSpec(
                function_id=0,
                args_ids=[1],
                kwargs_ids={"y": 2},
            )
        ],
        "resources": ResourceMap(
            functions={0: "mock_function_uri"},
            inputs={1: "mock_input_uri"},
            hooks={0: "mock_hooks_uri"},
        ),
        "task_group_metadata": {"dispatch_id": "1", "node_ids": ["1"], "task_group_id": "1"},
        "expected_output_uris": [("mock_path", "mock_path", "mock_path", "mock_path")],
        "expected_server_url": "mock_server_url",
        "expected_future_cancelled": False,
    },
    {
        "id": "future_cancelled",
        "task_specs": [
            TaskSpec(
                function_id=0,
                args_ids=[1],
                kwargs_ids={"y": 2},
            )
        ],
        "resources": ResourceMap(
            functions={0: "mock_function_uri"},
            inputs={1: "mock_input_uri"},
            hooks={0: "mock_hooks_uri"},
        ),
        "task_group_metadata": {"dispatch_id": "1", "node_ids": ["1"], "task_group_id": "1"},
        "expected_output_uris": [("mock_path", "mock_path", "mock_path", "mock_path")],
        "expected_server_url": "mock_server_url",
        "expected_future_cancelled": True,
    },
]


@pytest.mark.parametrize("test_case", test_cases, ids=[tc["id"] for tc in test_cases])
def test_send_internal(
    test_case,
    mock_os_path_join,
    mock_format_server_url,
    mock_future,
    mock_proc_pool_submit,
):
    """Test the internal _send function of LocalExecutor"""

    local_exec = LocalExecutor()

    # Arrange
    local_exec.cache_dir = "mock_cache_dir"
    mock_future.cancelled.return_value = test_case["expected_future_cancelled"]

    # Act
    local_exec._send(
        test_case["task_specs"],
        test_case["resources"],
        test_case["task_group_metadata"],
    )

    # Assert
    mock_os_path_join.assert_called()
    mock_format_server_url.assert_called_once_with()
    mock_proc_pool_submit.assert_called_once_with(
        run_task_group,
        list(map(lambda t: t.dict(), test_case["task_specs"])),
        test_case["expected_output_uris"],
        "mock_cache_dir",
        test_case["task_group_metadata"],
        test_case["expected_server_url"],
    )


@pytest.mark.asyncio
async def test_send(mocker):
    """Test the send function of LocalExecutor"""

    local_exec = LocalExecutor()

    # Arrange
    task_group_metadata = {"dispatch_id": "1", "node_ids": ["1", "2"]}
    task_spec = TaskSpec(
        function_id=0,
        args_ids=[1],
        kwargs_ids={"y": 2},
    )
    resource = ResourceMap(
        functions={0: "mock_function_uri"},
        inputs={1: "mock_input_uri"},
        hooks={0: "mock_hooks_uri"},
    )

    mock_loop = mocker.Mock()

    mock_get_running_loop = mocker.patch(
        "covalent.executor.executor_plugins.local.asyncio.get_running_loop",
        return_value=mock_loop,
    )
    mock_get_running_loop.return_value.run_in_executor = mocker.AsyncMock()

    await local_exec.send(
        [task_spec],
        resource,
        task_group_metadata,
    )

    mock_get_running_loop.assert_called_once()

    mock_get_running_loop.return_value.run_in_executor.assert_awaited_once_with(
        None,
        local_exec._send,
        [task_spec],
        resource,
        task_group_metadata,
    )


# Test data
test_data = [
    # Happy path tests
    {
        "id": "HP1",
        "task_group_metadata": {"dispatch_id": "1", "node_ids": ["1", "2"]},
        "data": {"status": StatusEnum.COMPLETED},
        "expected_status": StatusEnum.COMPLETED,
    },
    {
        "id": "HP2",
        "task_group_metadata": {"dispatch_id": "2", "node_ids": ["3", "4"]},
        "data": {"status": StatusEnum.FAILED},
        "expected_status": StatusEnum.FAILED,
    },
    # Edge case tests
    {
        "id": "EC1",
        "task_group_metadata": {"dispatch_id": "3", "node_ids": []},
        "data": {"status": StatusEnum.COMPLETED},
        "expected_status": StatusEnum.COMPLETED,
    },
    {
        "id": "EC2",
        "task_group_metadata": {"dispatch_id": "4", "node_ids": ["5"]},
        "data": None,
        "expected_status": RESULT_STATUS.CANCELLED,
    },
]


@pytest.mark.parametrize("test_case", test_data, ids=[tc["id"] for tc in test_data])
def test_receive_internal(test_case):
    """Test the internal _receive function of LocalExecutor"""

    local_exec = LocalExecutor()

    # Arrange
    task_group_metadata = test_case["task_group_metadata"]
    data = test_case["data"]
    expected_status = test_case["expected_status"]

    # Act
    task_results = local_exec._receive(task_group_metadata, data)

    # Assert
    for task_result in task_results:
        assert task_result.status == expected_status


@pytest.mark.asyncio
async def test_receive(mocker):
    """Test the receive function of LocalExecutor"""

    local_exec = LocalExecutor()

    # Arrange
    task_group_metadata = {"dispatch_id": "1", "node_ids": ["1", "2"]}
    test_data = {"status": StatusEnum.COMPLETED}

    mock_loop = mocker.Mock()

    mock_get_running_loop = mocker.patch(
        "covalent.executor.executor_plugins.local.asyncio.get_running_loop",
        return_value=mock_loop,
    )
    mock_get_running_loop.return_value.run_in_executor = mocker.AsyncMock()

    await local_exec.receive(
        task_group_metadata,
        test_data,
    )

    mock_get_running_loop.assert_called_once()

    mock_get_running_loop.return_value.run_in_executor.assert_awaited_once_with(
        None,
        local_exec._receive,
        task_group_metadata,
        test_data,
    )
