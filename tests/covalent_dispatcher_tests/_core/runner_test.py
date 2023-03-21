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

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.data_manager import get_result_object
from covalent_dispatcher._core.runner import (
    _build_sublattice_graph,
    _cancel_task,
    _dispatch_sublattice,
    _gather_deps,
    _get_cancel_requested,
    _get_metadata_for_nodes,
    _post_process,
    _postprocess_workflow,
    _run_abstract_task,
    _run_task,
    cancel_tasks,
)
from covalent_dispatcher._db import update
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
        workflow_executor=["local", {}],
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
        "covalent_dispatcher._core.runner._get_cancel_requested",
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
        selected_executor=["local", {}],
        workflow_executor=["local", {}],
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
        selected_executor=["nonexistent", {}],
        call_before=[],
        call_after=[],
        node_name="test_node",
        workflow_executor=["local", {}],
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
        selected_executor=["local", {}],
        call_before=[],
        call_after=[],
        node_name="task",
        workflow_executor=["local", {}],
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

    execution_result = _post_process(compute_energy, encoded_node_outputs)

    assert execution_result == compute_energy()


@pytest.mark.asyncio
async def test_postprocess_workflow(mocker):
    """Unit test for _postprocess_workflow"""

    result_object = get_mock_result()
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


def test_build_sublattice_graph():
    """
    Test building a sublattice graph
    """

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    parent_metadata = {
        "executor": "parent_executor",
        "executor_data": {},
        "workflow_executor": "my_postprocessor",
        "workflow_executor_data": {},
        "deps": {"bash": None, "pip": None},
        "call_before": [],
        "call_after": [],
        "triggers": None,
        "results_dir": None,
    }

    json_lattice = _build_sublattice_graph(workflow, parent_metadata, 1)
    lattice = Lattice.deserialize_from_json(json_lattice)

    assert list(lattice.transport_graph._graph.nodes) == [0, 1]
    for k in lattice.metadata.keys():
        # results_dir will be deprecated soon
        if k != "results_dir":
            assert parent_metadata[k] == lattice.metadata[k]


@pytest.mark.asyncio
async def test_dispatch_sublattice(test_db, mocker):
    """
    Test dispatching a sublattice and assert any exceptions raised
    """

    @ct.electron(executor="local")
    def task(x):
        return x

    @ct.lattice(executor="local", workflow_executor="local")
    def sub_workflow(x):
        return task(x)

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch")
    mocker.patch("covalent_dispatcher._db.jobdb.workflow_db", test_db)
    result_object = get_mock_result()
    update.persist(result_object)

    serialized_callable = ct.TransportableObject(sub_workflow)
    inputs = {"args": [ct.TransportableObject(2)], "kwargs": {}}

    sub_dispatch_id = await _dispatch_sublattice(
        parent_result_object=result_object,
        parent_node_id=2,
        parent_electron_id=1,
        inputs=inputs,
        serialized_callable=serialized_callable,
        workflow_executor=["local", {}],
    )
    sub_result = get_result_object(sub_dispatch_id)
    assert sub_result.dispatch_id == sub_dispatch_id

    # check that sublattice inherits parent lattice's bash dep
    sub_bash_dep = sub_result.lattice.metadata["deps"]["bash"]["attributes"]["commands"]
    assert sub_bash_dep[0] == "ls"
    assert sub_result._electron_id == 1

    # check that sublattice's explicit bash dep overrides parent lattice's bash dep
    sub_workflow.metadata["deps"]["bash"] = ct.DepsBash(["pwd"])
    serialized_callable = ct.TransportableObject(sub_workflow)
    sub_dispatch_id = await _dispatch_sublattice(
        parent_result_object=result_object,
        parent_node_id=2,
        parent_electron_id=1,
        inputs=inputs,
        serialized_callable=serialized_callable,
        workflow_executor=["local", {}],
    )
    sub_result = get_result_object(sub_dispatch_id)
    assert sub_result.dispatch_id == sub_dispatch_id

    # check that sublattice inherits parent lattice's bash dep
    sub_bash_dep = sub_result.lattice.metadata["deps"]["bash"]["attributes"]["commands"]
    assert sub_bash_dep[0] == "pwd"

    # Check handling of invalid workflow executors

    with pytest.raises(RuntimeError):
        sub_dispatch_id = await _dispatch_sublattice(
            parent_result_object=result_object,
            parent_node_id=2,
            parent_electron_id=1,
            inputs=inputs,
            serialized_callable=serialized_callable,
            workflow_executor=["client", {}],
        )

    with pytest.raises(RuntimeError):
        sub_dispatch_id = await _dispatch_sublattice(
            parent_result_object=result_object,
            parent_node_id=2,
            parent_electron_id=1,
            inputs=inputs,
            serialized_callable=serialized_callable,
            workflow_executor=["fake_executor", {}],
        )


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
    mock_executor_manager = mocker.patch(
        "covalent_dispatcher._core.runner._executor_manager.get_executor",
        return_value=mock_executor,
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
    mock_executor_manager.assert_called_with(executor)
    mock_executor.from_dict.assert_called_with(executor_data)
    mock_executor._init_runtime.assert_called()
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
    mock_executor_manager = mocker.patch(
        "covalent_dispatcher._core.runner._executor_manager.get_executor",
        return_value=mock_executor,
    )
    mock_set_cancel_result = mocker.patch("covalent_dispatcher._core.runner.set_cancel_result")

    dispatch_id = "abcd"
    task_id = 0
    executor = "mock_executor"
    executor_data = {}
    job_handle = "42"

    task_metadata = {"dispatch_id": dispatch_id, "node_id": task_id}

    cancel_result = await _cancel_task(dispatch_id, task_id, executor, executor_data, job_handle)
    assert mock_app_log.call_count == 3
    mock_executor_manager.assert_called_with(executor)
    mock_executor.from_dict.assert_called_with(executor_data)
    mock_executor._init_runtime.assert_called()
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
        "covalent_dispatcher._core.runner.get_jobs_metadata", return_value=AsyncMock()
    )

    await _get_cancel_requested(dispatch_id, task_id)

    mock_get_jobs_metadata.assert_awaited_with(dispatch_id, [task_id])
