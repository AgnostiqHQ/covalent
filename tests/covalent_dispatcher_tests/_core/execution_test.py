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
Integration tests for the dispatcher, runner, and result modules
"""

import asyncio

import pytest

import covalent as ct
from covalent._results_manager import Result
from covalent._shared_files.defaults import sublattice_prefix
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.dispatcher import _dispatch_sync_sublattice, run_workflow
from covalent_dispatcher._core.runner import _run_task
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

    @ct.lattice(results_dir=TEST_RESULTS_DIR)
    def pipeline(x):
        res1 = task(x)
        res2 = task(res1)
        return res2

    pipeline.build_graph(x="absolute")
    received_workflow = Lattice.deserialize_from_json(pipeline.serialize_to_json())
    result_object = Result(
        received_workflow, pipeline.metadata["results_dir"], "pipeline_workflow"
    )

    return result_object


@pytest.mark.asyncio
async def test_run_workflow_with_failing_nonleaf(mocker):
    """Test running workflow with a failing intermediate node"""

    @ct.electron
    def failing_task(x):
        assert False

    @ct.lattice
    def workflow(x):
        res1 = failing_task(x)
        res2 = failing_task(res1)
        return res2

    from covalent._workflow.lattice import Lattice

    workflow.build_graph(5)

    json_lattice = workflow.serialize_to_json()
    dispatch_id = "asdf"
    lattice = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lattice, lattice.metadata["results_dir"])
    result_object._dispatch_id = dispatch_id
    result_object._root_dispatch_id = dispatch_id
    result_object._initialize_nodes()

    # patch all methods that reference a DB
    mocker.patch("covalent_dispatcher._db.upsert._lattice_data")
    mocker.patch("covalent_dispatcher._db.upsert._electron_data")
    mocker.patch("covalent_dispatcher._db.update.persist")
    mocker.patch(
        "covalent._results_manager.result.Result._get_node_name", return_value="failing_task"
    )
    mocker.patch(
        "covalent._results_manager.result.Result._get_node_error", return_value="AssertionError"
    )
    mocker.patch("covalent_dispatcher._core.dispatcher.update_lattices_data")
    mocker.patch("covalent_dispatcher._core.dispatcher.write_lattice_error")
    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.resultsvc.unregister_dispatch"
    )
    mocker.patch(
        "covalent_dispatcher._core.runner.resultsvc.get_result_object", return_value=result_object
    )

    status_queue = asyncio.Queue()
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_status_queue", return_value=status_queue
    )

    update.persist(result_object)
    result_object = await run_workflow(result_object)
    mock_unregister.assert_called_with(result_object.dispatch_id)
    assert result_object.status == Result.FAILED


@pytest.mark.asyncio
async def test_run_workflow_with_failing_leaf(mocker):
    """Test running workflow with a failing leaf node"""

    @ct.electron
    def failing_task(x):
        assert False
        return x

    @ct.lattice
    def workflow(x):
        res1 = failing_task(x)
        return res1

    from covalent._workflow.lattice import Lattice

    workflow.build_graph(5)

    json_lattice = workflow.serialize_to_json()
    dispatch_id = "asdf"
    lattice = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lattice, lattice.metadata["results_dir"])
    result_object._dispatch_id = dispatch_id
    result_object._root_dispatch_id = dispatch_id
    result_object._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.upsert._lattice_data")
    mocker.patch("covalent_dispatcher._db.upsert._electron_data")
    mocker.patch("covalent_dispatcher._db.update.persist")
    mocker.patch(
        "covalent._results_manager.result.Result._get_node_name", return_value="failing_task"
    )
    mocker.patch(
        "covalent._results_manager.result.Result._get_node_error", return_value="AssertionError"
    )
    mocker.patch("covalent_dispatcher._core.dispatcher.update_lattices_data")
    mocker.patch("covalent_dispatcher._core.dispatcher.write_lattice_error")
    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.resultsvc.unregister_dispatch"
    )
    mocker.patch(
        "covalent_dispatcher._core.runner.resultsvc.get_result_object", return_value=result_object
    )

    status_queue = asyncio.Queue()
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_status_queue", return_value=status_queue
    )

    update.persist(result_object)

    result_object = await run_workflow(result_object)
    mock_unregister.assert_called_with(result_object.dispatch_id)
    assert result_object.status == Result.FAILED


async def test_run_workflow_does_not_deserialize(mocker):
    """Check that dispatcher does not deserialize user data when using
    out-of-process `workflow_executor`"""

    from dask.distributed import LocalCluster

    from covalent._workflow.lattice import Lattice
    from covalent.executor import DaskExecutor

    lc = LocalCluster()
    dask_exec = DaskExecutor(lc.scheduler_address)

    @ct.electron(executor=dask_exec)
    def task(x):
        return x

    @ct.lattice(executor=dask_exec, workflow_executor=dask_exec)
    def workflow(x):
        # Exercise both sublatticing and postprocessing
        sublattice_task = ct.lattice(task, workflow_executor=dask_exec)
        res1 = ct.electron(sublattice_task(x), executor=dask_exec)
        return res1

    workflow.build_graph(5)

    json_lattice = workflow.serialize_to_json()
    dispatch_id = "asdf"
    lattice = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lattice, lattice.metadata["results_dir"])
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.datastore.DataStore.factory", return_value=test_db)
    mocker.patch(
        "covalent_dispatcher._core.runner.resultsvc.get_result_object", return_value=result_object
    )
    update.persist(result_object)

    mock_to_deserialize = mocker.patch("covalent.TransportableObject.get_deserialized")

    result_object = await run_workflow(result_object)

    mock_to_deserialize.assert_not_called()
    assert result_object.status == Result.COMPLETED


@pytest.mark.asyncio
async def test_run_workflow_with_client_side_postprocess(test_db, mocker):
    """Check that run_workflow handles "client" workflow_executor for
    postprocessing"""

    dispatch_id = "asdf"
    result_object = get_mock_result()
    result_object.lattice.set_metadata("workflow_executor", "client")
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.resultsvc.unregister_dispatch"
    )
    mocker.patch(
        "covalent_dispatcher._core.runner.resultsvc.get_result_object", return_value=result_object
    )

    status_queue = asyncio.Queue()
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_status_queue", return_value=status_queue
    )

    update.persist(result_object)

    result_object = await run_workflow(result_object)
    mock_unregister.assert_called_with(result_object.dispatch_id)
    assert result_object.status == Result.PENDING_POSTPROCESSING


@pytest.mark.asyncio
async def test_run_workflow_with_failed_postprocess(test_db, mocker):
    """Check that run_workflow handles postprocessing failures"""

    dispatch_id = "asdf"
    result_object = get_mock_result()
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.resultsvc.unregister_dispatch"
    )
    mocker.patch(
        "covalent_dispatcher._core.runner.resultsvc.get_result_object", return_value=result_object
    )

    update.persist(result_object)

    status_queue = asyncio.Queue()
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_status_queue", return_value=status_queue
    )

    def failing_workflow(x):
        assert False

    result_object.lattice.set_metadata("workflow_executor", "bogus")
    result_object = await run_workflow(result_object)
    mock_unregister.assert_called_with(result_object.dispatch_id)

    assert result_object.status == Result.POSTPROCESSING_FAILED

    result_object.lattice.workflow_function = ct.TransportableObject(failing_workflow)
    result_object.lattice.set_metadata("workflow_executor", "local")

    result_object = await run_workflow(result_object)
    mock_unregister.assert_called_with(result_object.dispatch_id)

    assert result_object.status == Result.POSTPROCESSING_FAILED


@pytest.mark.asyncio
async def test_dispatch_sync_sublattice(test_db, mocker):
    @ct.electron(executor="local")
    def task(x):
        return x

    @ct.lattice(executor="local", workflow_executor="local")
    def sub_workflow(x):
        return task(x)

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._core.dispatcher.resultsvc.unregister_dispatch")

    result_object = get_mock_result()

    serialized_callable = ct.TransportableObject(sub_workflow)
    inputs = {"args": [ct.TransportableObject(2)], "kwargs": {}}

    sub_result = await _dispatch_sync_sublattice(
        parent_result_object=result_object,
        parent_electron_id=1,
        inputs=inputs,
        serialized_callable=serialized_callable,
        workflow_executor=["local", {}],
    )
    assert sub_result.result == 2

    # Check handling of invalid workflow executors

    sub_result = await _dispatch_sync_sublattice(
        parent_result_object=result_object,
        parent_electron_id=1,
        inputs=inputs,
        serialized_callable=serialized_callable,
        workflow_executor=["client", {}],
    )
    assert sub_result is None

    sub_result = await _dispatch_sync_sublattice(
        parent_result_object=result_object,
        parent_electron_id=1,
        inputs=inputs,
        serialized_callable=serialized_callable,
        workflow_executor=["fake_executor", {}],
    )
    assert sub_result is None


@pytest.mark.asyncio
async def test_run_task_sublattice_handling(test_db, mocker):

    result_object = get_mock_result()
    sub_result_object = get_mock_result()
    sub_result_object._dispatch_id = "sublattice_workflow"
    sub_result_object._result = ct.TransportableObject(5)
    sub_result_object._status = Result.COMPLETED

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mock_get_sublattice_electron_id = mocker.patch(
        "covalent_dispatcher._core.runner.get_sublattice_electron_id", return_value=1
    )
    mock_dispatch_sync = mocker.patch(
        "covalent_dispatcher._core.dispatcher._dispatch_sync_sublattice",
        return_value=sub_result_object,
    )

    inputs = {"args": [], "kwargs": {}}

    node_result = await _run_task(
        result_object=result_object,
        node_id=1,
        inputs=inputs,
        serialized_callable=None,
        selected_executor=["local", {}],
        call_before=[],
        call_after=[],
        node_name=sublattice_prefix,
        workflow_executor=["local", {}],
    )

    mock_get_sublattice_electron_id.assert_called_once()
    mock_dispatch_sync.assert_awaited_once()
    assert node_result["output"].get_deserialized() == 5

    # Test failed sublattice workflows
    sub_result_object._status = Result.FAILED
    mock_dispatch_sync = mocker.patch(
        "covalent_dispatcher._core.dispatcher._dispatch_sync_sublattice",
        return_value=sub_result_object,
    )
    node_result = await _run_task(
        result_object=result_object,
        node_id=1,
        inputs=inputs,
        serialized_callable=None,
        selected_executor=["local", {}],
        call_before=[],
        call_after=[],
        node_name=sublattice_prefix,
        workflow_executor=["local", {}],
    )

    mock_dispatch_sync.assert_awaited_once()
    assert node_result["status"] == Result.FAILED

    mock_dispatch_sync = mocker.patch(
        "covalent_dispatcher._core.dispatcher._dispatch_sync_sublattice", return_value=None
    )
    node_result = await _run_task(
        result_object=result_object,
        node_id=1,
        inputs=inputs,
        serialized_callable=None,
        selected_executor=["local", {}],
        call_before=[],
        call_after=[],
        node_name=sublattice_prefix,
        workflow_executor=["local", {}],
    )

    assert node_result["status"] == Result.FAILED
