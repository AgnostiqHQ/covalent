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
from covalent_dispatcher._core.runner import (
    _gather_deps,
    _post_process,
    _postprocess_workflow,
    _run_abstract_task,
    _run_task,
)
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


def test_gather_deps(mocker, test_db):
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

    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_result_object",
        return_value=result_object,
    )

    before, after = _gather_deps(result_object, 0)
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
    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object",
        return_value=result_object,
    )
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

    node_result = await _run_task(
        result_object=result_object,
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

    node_result = await _run_task(
        result_object=result_object,
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


def test_post_process():
    """Test post-processing of results."""

    import covalent as ct

    @ct.electron
    def construct_cu_slab(x):
        return x

    @ct.electron
    def compute_system_energy(x):
        return x

    @ct.electron
    def construct_n_molecule(x):
        return x

    @ct.electron
    def get_relaxed_slab(x):
        return x

    @ct.lattice
    def compute_energy():
        N2 = construct_n_molecule(1)
        e_N2 = compute_system_energy(N2)

        slab = construct_cu_slab(2)
        e_slab = compute_system_energy(slab)

        relaxed_slab = get_relaxed_slab(3)
        e_relaxed_slab = compute_system_energy(relaxed_slab)

        return (N2, e_N2, slab, e_slab, relaxed_slab, e_relaxed_slab)

    compute_energy.build_graph()

    node_outputs = {
        "construct_n_molecule(0)": 1,
        ":parameter:1(1)": 1,
        "compute_system_energy(2)": 1,
        "construct_cu_slab(3)": 2,
        ":parameter:2(4)": 2,
        "compute_system_energy(5)": 2,
        "get_relaxed_slab(6)": 3,
        ":parameter:3(7)": 3,
        "compute_system_energy(8)": 3,
    }

    encoded_node_outputs = {
        k: ct.TransportableObject.make_transportable(v) for k, v in node_outputs.items()
    }

    inputs = {"args": [], "kwargs": {}}

    execution_result = _post_process(
        compute_energy.workflow_function.get_deserialized(), inputs, encoded_node_outputs
    )

    assert execution_result == compute_energy()


@pytest.mark.asyncio
async def test_postprocess_workflow(mocker, test_db):
    """Unit test for _postprocess_workflow"""

    sdkres = get_mock_result()
    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    sdkres._initialize_nodes()
    result_object = get_mock_srvresult(sdkres, test_db)

    node_result = {"node_id": -1, "status": Result.COMPLETED, "output": 42}
    failed_node_result = {"node_id": -1, "status": Result.FAILED, "stderr": "OOM", "error": None}
    mock_run_task = mocker.patch(
        "covalent_dispatcher._core.runner._run_task", return_value=node_result
    )
    mock_get_node_outputs = mocker.patch(
        "covalent._results_manager.result.Result.get_all_node_outputs", return_value=[0]
    )
    mocker.patch("covalent_dispatcher._db.upsert._lattice_data")

    await _postprocess_workflow(result_object)
    assert result_object._status == Result.COMPLETED
    assert result_object._result == 42

    mock_run_task = mocker.patch(
        "covalent_dispatcher._core.runner._run_task", return_value=failed_node_result
    )
    await _postprocess_workflow(result_object)
    assert result_object._status == Result.POSTPROCESSING_FAILED
    assert "OOM" in result_object._error
