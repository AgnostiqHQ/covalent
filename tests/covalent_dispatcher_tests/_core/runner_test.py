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

"""
Tests for the core functionality of the runner.
"""


import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from mock import call

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.runner import (
    _cancel_task,
    _gather_deps,
    _get_metadata_for_nodes,
    _run_abstract_task,
    _run_task,
    cancel_tasks,
    get_executor,
)
from covalent_dispatcher._core.runner_modules.executor_proxy import _get_cancel_requested
from covalent_dispatcher._db.datastore import DataStore

TEST_RESULTS_DIR = "/tmp/results"


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def get_mock_result() -> Result:
    """Construct a mock result object corresponding to a lattice."""

    import sys

    @ct.electron(executor="local")
    def task(x):
        print(f"stdout: {x}")
        print("Error!", file=sys.stderr)
        return x

    @ct.lattice(deps_bash=ct.DepsBash(["ls"]))
    def pipeline(x):
        res1 = task(x)
        res2 = task(res1)
        return res2

    pipeline.build_graph(x="absolute")
    received_workflow = Lattice.deserialize_from_json(pipeline.serialize_to_json())
    result_object = Result(received_workflow, "pipeline_workflow")
    result_object._initialize_nodes()

    return result_object


def test_get_executor(mocker):
    """Test that get_executor returns the correct executor"""

    executor_manager_mock = mocker.patch("covalent_dispatcher._core.runner._executor_manager")
    executor = get_executor(["local", {"mock-key": "mock-value"}], "mock-loop", "mock-pool")
    assert executor_manager_mock.get_executor.mock_calls == [
        call("local"),
        call().from_dict({"mock-key": "mock-value"}),
        call()._init_runtime(loop="mock-loop", cancel_pool="mock-pool"),
    ]
    assert executor == executor_manager_mock.get_executor()


def test_gather_deps():
    """Test internal _gather_deps for assembling deps into call_before and
    call_after"""

    def square(x):
        return x * x

    @ct.electron(
        deps_bash=ct.DepsBash("ls -l"),
        deps_pip=ct.DepsPip(["pandas"]),
        call_before=[ct.DepsCall(square, [5])],
        call_after=[ct.DepsCall(square, [3])],
    )
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph(5)

    received_workflow = Lattice.deserialize_from_json(workflow.serialize_to_json())
    result_object = Result(received_workflow, "asdf")

    before, after = _gather_deps(result_object, 0)
    assert len(before) == 3
    assert len(after) == 1


@pytest.mark.asyncio
async def test_run_abstract_task_exception_handling(mocker):
    """Test that exceptions from resolving abstract inputs are handled"""

    result_object = get_mock_result()
    inputs = {"args": [], "kwargs": {}}
    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )

    mocker.patch(
        "covalent_dispatcher._core.runner._get_task_input_values",
        side_effect=RuntimeError(),
    )

    node_result = await _run_abstract_task(
        dispatch_id=result_object.dispatch_id,
        node_id=0,
        node_name="test_node",
        abstract_inputs=inputs,
        executor=["local", {}],
    )

    assert node_result["status"] == Result.FAILED


@pytest.mark.asyncio
async def test_run_abstract_task_get_cancel_requested(mocker):
    """Test that get_cancel_requested is properly handled"""
    mock_result = MagicMock()

    result_object = get_mock_result()
    inputs = {"args": [], "kwargs": {}}
    mock_app_log = mocker.patch("covalent_dispatcher._core.runner.app_log.debug")
    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )
    mock_get_task_input_values = mocker.patch(
        "covalent_dispatcher._core.runner._get_task_input_values",
        side_effect=RuntimeError(),
    )
    mock_get_cancel_requested = mocker.patch(
        "covalent_dispatcher._core.runner_modules.executor_proxy._get_cancel_requested",
        return_value=AsyncMock(return_value=True),
    )
    mock_generate_node_result = mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.generate_node_result",
        return_value=mock_result,
    )

    node_result = await _run_abstract_task(
        dispatch_id=result_object.dispatch_id,
        node_id=0,
        node_name="test_node",
        abstract_inputs=inputs,
        executor=["local", {}],
    )

    mock_get_result.assert_called_with(result_object.dispatch_id)
    mock_get_cancel_requested.assert_awaited_once_with(result_object.dispatch_id, 0)
    mock_generate_node_result.assert_called()
    mock_app_log.assert_called_with(f"Don't run cancelled task {result_object.dispatch_id}:0")
    assert node_result == mock_result


@pytest.mark.asyncio
async def test_run_task_executor_exception_handling(mocker):
    """Test that exceptions from initializing executors are caught"""

    result_object = get_mock_result()
    inputs = {"args": [], "kwargs": {}}
    mock_get_executor = mocker.patch(
        "covalent_dispatcher._core.runner._executor_manager.get_executor",
        side_effect=Exception(),
    )

    node_result = await _run_task(
        result_object=result_object,
        node_id=1,
        inputs=inputs,
        serialized_callable=None,
        executor=["nonexistent", {}],
        call_before=[],
        call_after=[],
        node_name="test_node",
    )

    assert node_result["status"] == Result.FAILED


@pytest.mark.asyncio
async def test_run_task_runtime_exception_handling(mocker):
    result_object = get_mock_result()
    inputs = {"args": [], "kwargs": {}}
    mock_executor = MagicMock()
    mock_executor._execute = AsyncMock(return_value=("", "", "error", True))
    mock_get_executor = mocker.patch(
        "covalent_dispatcher._core.runner._executor_manager.get_executor",
        return_value=mock_executor,
    )

    node_result = await _run_task(
        result_object=result_object,
        node_id=1,
        inputs=inputs,
        serialized_callable=None,
        executor=["local", {}],
        call_before=[],
        call_after=[],
        node_name="task",
    )

    mock_executor._execute.assert_awaited_once()

    assert node_result["stderr"] == "error"


@pytest.mark.asyncio
async def test__cancel_task(mocker):
    """
    Test module private _cancel_task method
    """
    mock_executor = AsyncMock()
    mock_executor.from_dict = MagicMock()
    mock_executor._init_runtime = MagicMock()
    mock_executor._cancel = AsyncMock()

    mock_app_log = mocker.patch("covalent_dispatcher._core.runner.app_log.debug")
    get_executor_mock = mocker.patch(
        "covalent_dispatcher._core.runner.get_executor", return_value=mock_executor
    )
    mock_set_cancel_result = mocker.patch("covalent_dispatcher._core.runner.set_cancel_result")

    dispatch_id = "abcd"
    task_id = 0
    executor = "mock_executor"
    executor_data = {}
    job_handle = "42"

    task_metadata = {"dispatch_id": dispatch_id, "node_id": task_id}

    await _cancel_task(dispatch_id, task_id, executor, executor_data, job_handle)

    assert mock_app_log.call_count == 2
    get_executor_mock.assert_called_once()
    mock_executor._cancel.assert_called_with(task_metadata, json.loads(job_handle))
    mock_set_cancel_result.assert_called()


@pytest.mark.asyncio
async def test__cancel_task_exception(mocker):
    """
    Test exception raised in module private _cancel task exception
    """
    mock_executor = AsyncMock()
    mock_executor.from_dict = MagicMock()
    mock_executor._init_runtime = MagicMock()
    mock_executor._cancel = AsyncMock(side_effect=Exception("cancel"))

    mock_app_log = mocker.patch("covalent_dispatcher._core.runner.app_log.debug")
    get_executor_mock = mocker.patch(
        "covalent_dispatcher._core.runner.get_executor", return_value=mock_executor
    )
    mocker.patch("covalent_dispatcher._core.runner.set_cancel_result")

    dispatch_id = "abcd"
    task_id = 0
    executor = "mock_executor"
    executor_data = {}
    job_handle = "42"

    task_metadata = {"dispatch_id": dispatch_id, "node_id": task_id}

    cancel_result = await _cancel_task(dispatch_id, task_id, executor, executor_data, job_handle)
    assert mock_app_log.call_count == 3
    get_executor_mock.assert_called_once()
    mock_executor._cancel.assert_called_with(task_metadata, json.loads(job_handle))
    assert cancel_result is False


@pytest.mark.asyncio
async def test_cancel_tasks(mocker):
    """
    Test cancelling multiple tasks
    """
    mock_get_jobs_metadata = mocker.patch(
        "covalent_dispatcher._core.runner.get_jobs_metadata", return_value=AsyncMock()
    )
    mock_get_metadata_for_nodes = mocker.patch(
        "covalent_dispatcher._core.runner._get_metadata_for_nodes", return_value=MagicMock()
    )

    dispatch_id = "abcd"
    task_ids = [0, 1]

    await cancel_tasks(dispatch_id, task_ids)

    mock_get_jobs_metadata.assert_awaited_with(dispatch_id, task_ids)
    mock_get_metadata_for_nodes.assert_called_with(dispatch_id, task_ids)


def test__get_metadata_for_nodes(mocker):
    """
    Test module private method for getting nodes metadata
    """
    dispatch_id = "abcd"
    node_ids = [0, 1]

    mock_get_result_object = mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=MagicMock()
    )
    _get_metadata_for_nodes(dispatch_id, node_ids)
    mock_get_result_object.assert_called_with(dispatch_id)


@pytest.mark.asyncio
async def test__get_cancel_requested(mocker):
    """
    Test module private method for querying if a task was requested to be cancelled
    """
    dispatch_id = "abcd"
    task_id = 0
    mock_get_jobs_metadata = mocker.patch(
        "covalent_dispatcher._core.runner_modules.executor_proxy.job_manager.get_jobs_metadata",
        return_value=AsyncMock(),
    )

    await _get_cancel_requested(dispatch_id, task_id)

    mock_get_jobs_metadata.assert_awaited_with(dispatch_id, [task_id])
