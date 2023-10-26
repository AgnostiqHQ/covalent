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

"""
Tests for the core functionality of the runner.
"""


from unittest.mock import AsyncMock, MagicMock

import pytest

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.runner import _run_abstract_task, _run_task
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

    return result_object


@pytest.mark.asyncio
async def test_run_abstract_task_exception_handling(mocker):
    """Test that exceptions from resolving abstract inputs are handled"""

    dispatch_id = "mock_dispatch"

    inputs = {"args": [], "kwargs": {}}

    mocker.patch("covalent_dispatcher._core.runner._gather_deps", side_effect=RuntimeError())
    mocker.patch(
        "covalent_dispatcher._core.data_manager.electron.get",
        return_value={"function": "function"},
    )

    node_result = await _run_abstract_task(
        dispatch_id=dispatch_id,
        node_id=0,
        node_name="test_node",
        abstract_inputs=inputs,
        selected_executor=["local", {}],
    )

    assert node_result["status"] == Result.FAILED


@pytest.mark.asyncio
async def test_run_task_runtime_exception_handling(mocker):
    inputs = {"args": [], "kwargs": {}}
    mock_executor = MagicMock()
    mock_executor._execute = AsyncMock(return_value=("", "", "error", Result.FAILED))
    mock_get_executor = mocker.patch(
        "covalent_dispatcher._core.runner.get_executor",
        return_value=mock_executor,
    )

    dispatch_id = "mock_dispatch"
    mocker.patch(
        "covalent_dispatcher._core.data_manager.dispatch.get",
        return_value={"results_dir": "/tmp/result"},
    )

    node_result = await _run_task(
        dispatch_id=dispatch_id,
        node_id=1,
        inputs=inputs,
        serialized_callable=None,
        selected_executor=["local", {}],
        call_before=[],
        call_after=[],
        node_name="task",
    )

    mock_executor._execute.assert_awaited_once()

    assert node_result["status"] == Result.FAILED
    assert node_result["stderr"] == "error"


@pytest.mark.asyncio
async def test_run_task_exception_handling(mocker):
    dispatch_id = "mock_dispatch"
    inputs = {"args": [], "kwargs": {}}
    mock_executor = MagicMock()
    mock_executor._execute = AsyncMock(side_effect=RuntimeError("error"))

    mock_get_executor = mocker.patch(
        "covalent_dispatcher._core.runner.get_executor",
        return_value=mock_executor,
    )

    mocker.patch(
        "covalent_dispatcher._core.data_manager.dispatch.get",
        return_value={"results_dir": "/tmp/result"},
    )
    mocker.patch("traceback.TracebackException.from_exception", return_value="error")
    node_result = await _run_task(
        dispatch_id=dispatch_id,
        node_id=1,
        inputs=inputs,
        serialized_callable=None,
        selected_executor=["local", {}],
        call_before=[],
        call_after=[],
        node_name="task",
    )

    mock_executor._execute.assert_awaited_once()

    assert node_result["status"] == Result.FAILED
    assert node_result["error"] == "error"


@pytest.mark.asyncio
async def test_run_task_executor_exception_handling(mocker):
    """Test that exceptions from initializing executors are caught"""

    dispatch_id = "mock_dispatch"
    inputs = {"args": [], "kwargs": {}}
    mock_get_executor = mocker.patch(
        "covalent_dispatcher._core.runner.get_executor",
        side_effect=Exception(),
    )

    mocker.patch(
        "covalent_dispatcher._core.data_manager.dispatch.get",
        return_value={"results_dir": "/tmp/result"},
    )

    node_result = await _run_task(
        dispatch_id=dispatch_id,
        node_id=1,
        inputs=inputs,
        serialized_callable=None,
        selected_executor=["nonexistent", {}],
        call_before=[],
        call_after=[],
        node_name="test_node",
    )

    assert node_result["status"] == Result.FAILED
