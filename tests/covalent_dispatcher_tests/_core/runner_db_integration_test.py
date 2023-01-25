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


from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.pool import StaticPool

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.runner import _gather_deps, _run_abstract_task, _run_task
from covalent_dispatcher._dal.result import Result as SRVResult
from covalent_dispatcher._dal.result import get_result_object
from covalent_dispatcher._db import update
from covalent_dispatcher._db.datastore import DataStore

TEST_RESULTS_DIR = "/tmp/results"


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
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


def get_mock_srvresult(sdkres, test_db) -> SRVResult:

    sdkres._initialize_nodes()

    update.persist(sdkres)

    return get_result_object(sdkres.dispatch_id)


@pytest.mark.asyncio
async def test_gather_deps(mocker, test_db):
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

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)
    workflow.build_graph(5)

    received_workflow = Lattice.deserialize_from_json(workflow.serialize_to_json())
    sdkres = Result(received_workflow, "asdf")
    result_object = get_mock_srvresult(sdkres, test_db)

    async def get_electron_attr(dispatch_id, node_id, key):
        return result_object.lattice.transport_graph.get_node_value(node_id, key)

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_electron_attribute",
        get_electron_attr,
    )

    before, after = await _gather_deps(result_object.dispatch_id, 0)
    assert len(before) == 3
    assert len(after) == 1


@pytest.mark.asyncio
async def test_run_abstract_task_exception_handling(mocker, test_db):
    """Test that exceptions from resolving abstract inputs are handled"""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    sdkres = get_mock_result()
    result_object = get_mock_srvresult(sdkres, test_db)

    inputs = {"args": [], "kwargs": {}}
    mock_get_task_input_values = mocker.patch(
        "covalent_dispatcher._core.runner._get_task_input_values",
        side_effect=RuntimeError(),
    )

    node_result = await _run_abstract_task(
        dispatch_id=result_object.dispatch_id,
        node_id=0,
        node_name="test_node",
        abstract_inputs=inputs,
        selected_executor=["local", {}],
    )

    assert node_result["status"] == Result.FAILED


@pytest.mark.asyncio
async def test_run_task_executor_exception_handling(mocker, test_db):
    """Test that exceptions from initializing executors are caught"""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    sdkres = get_mock_result()
    result_object = get_mock_srvresult(sdkres, test_db)

    inputs = {"args": [], "kwargs": {}}
    mock_get_executor = mocker.patch(
        "covalent_dispatcher._core.runner.get_executor",
        side_effect=Exception(),
    )

    async def get_electron_attr(dispatch_id, node_id, key):
        return result_object.lattice.transport_graph.get_node_value(dispatch_id, node_id, key)

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_electron_attribute",
        get_electron_attr,
    )

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_dispatch_attributes",
        return_value={"results_dir": "/tmp/result"},
    )

    node_result = await _run_task(
        dispatch_id=result_object.dispatch_id,
        node_id=1,
        inputs=inputs,
        serialized_callable=None,
        selected_executor=["nonexistent", {}],
        call_before=[],
        call_after=[],
        node_name="test_node",
    )

    assert node_result["status"] == Result.FAILED


@pytest.mark.asyncio
async def test_run_task_runtime_exception_handling(mocker, test_db):

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    sdkres = get_mock_result()
    result_object = get_mock_srvresult(sdkres, test_db)

    inputs = {"args": [], "kwargs": {}}
    mock_executor = MagicMock()
    mock_executor._execute = AsyncMock(return_value=("", "", "error", True))
    mock_get_executor = mocker.patch(
        "covalent_dispatcher._core.runner.get_executor",
        return_value=mock_executor,
    )

    async def get_electron_attr(dispatch_id, node_id, key):
        return result_object.lattice.transport_graph.get_node_value(dispatch_id, node_id, key)

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_electron_attribute",
        get_electron_attr,
    )
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_dispatch_attributes",
        return_value={"results_dir": "/tmp/result"},
    )

    node_result = await _run_task(
        dispatch_id=result_object.dispatch_id,
        node_id=1,
        inputs=inputs,
        serialized_callable=None,
        selected_executor=["local", {}],
        call_before=[],
        call_after=[],
        node_name="task",
    )

    mock_executor._execute.assert_awaited_once()

    assert node_result["stderr"] == "error"


@pytest.mark.asyncio
async def test_run_task_exception_handling(mocker, test_db):

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    sdkres = get_mock_result()
    result_object = get_mock_srvresult(sdkres, test_db)

    inputs = {"args": [], "kwargs": {}}
    mock_executor = MagicMock()
    mock_executor._execute = AsyncMock(side_effect=RuntimeError())

    mock_get_executor = mocker.patch(
        "covalent_dispatcher._core.runner.get_executor",
        return_value=mock_executor,
    )

    async def get_electron_attr(dispatch_id, node_id, key):
        return result_object.lattice.transport_graph.get_node_value(dispatch_id, node_id, key)

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_electron_attribute",
        get_electron_attr,
    )
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_dispatch_attributes",
        return_value={"results_dir": "/tmp/result"},
    )
    mocker.patch("traceback.TracebackException.from_exception", return_value="error")
    node_result = await _run_task(
        dispatch_id=result_object.dispatch_id,
        node_id=1,
        inputs=inputs,
        serialized_callable=None,
        selected_executor=["local", {}],
        call_before=[],
        call_after=[],
        node_name="task",
    )

    mock_executor._execute.assert_awaited_once()

    assert node_result["error"] == "error"
