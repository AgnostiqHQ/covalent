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
import tempfile
from functools import partial
from unittest.mock import MagicMock

import pytest

import covalent as ct
from covalent._shared_files import TaskRuntimeError
from covalent._shared_files.exceptions import TaskCancelledError
from covalent._workflow.transport import TransportableObject
from covalent.executor.base import wrapper_fn
from covalent.executor.executor_plugins.local import LocalExecutor


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
