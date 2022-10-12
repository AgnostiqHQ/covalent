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
Tests for the core functionality of the dispatcher.
"""


import asyncio
from asyncio import Queue
from typing import Dict, List

import cloudpickle as pickle
import pytest

import covalent as ct
from covalent._results_manager import Result
from covalent._shared_files.defaults import sublattice_prefix
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.execution import (
    _build_sublattice_graph,
    _dispatch_sync_sublattice,
    _gather_deps,
    _get_task_inputs,
    _handle_cancelled_node,
    _handle_completed_node,
    _handle_failed_node,
    _initialize_deps_and_queue,
    _plan_workflow,
    _post_process,
    _run_task,
    _update_node_result,
    initialize_result_object,
    run_workflow,
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


def test_initialize_result_object(mocker, test_db):
    """Test the `initialize_result_object` function"""

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph(1)
    json_lattice = workflow.serialize_to_json()
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", return_value=test_db)
    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", return_value=test_db)
    result_object = get_mock_result()

    mock_persist = mocker.patch("covalent_dispatcher._db.update.persist")

    sub_result_object = initialize_result_object(
        json_lattice=json_lattice, parent_result_object=result_object, parent_electron_id=5
    )

    mock_persist.assert_called_with(sub_result_object, electron_id=5)
    assert sub_result_object._root_dispatch_id == result_object.dispatch_id


def test_plan_workflow():
    """Test workflow planning method."""

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.metadata["schedule"] = True
    received_workflow = Lattice.deserialize_from_json(workflow.serialize_to_json())
    result_object = Result(received_workflow, "/tmp", "asdf")
    _plan_workflow(result_object=result_object)

    # Updated transport graph post planning
    updated_tg = pickle.loads(result_object.lattice.transport_graph.serialize(metadata_only=True))

    assert updated_tg["lattice_metadata"]["schedule"]


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


def test_get_task_inputs():
    """Test _get_task_inputs for both dicts and list parameter types"""

    @ct.electron
    def list_task(arg: List):
        return len(arg)

    @ct.electron
    def dict_task(arg: Dict):
        return len(arg)

    @ct.electron
    def multivariable_task(x, y):
        return x, y

    @ct.lattice
    def list_workflow(arg):
        return list_task(arg)

    @ct.lattice
    def dict_workflow(arg):
        return dict_task(arg)

    #    1   2
    #     \   \
    #      0   3
    #     / /\/
    #     4   5

    @ct.electron
    def identity(x):
        return x

    @ct.lattice
    def multivar_workflow(x, y):
        electron_x = identity(x)
        electron_y = identity(y)
        res1 = multivariable_task(electron_x, electron_y)
        res2 = multivariable_task(electron_y, electron_x)
        res3 = multivariable_task(electron_y, electron_x)
        res4 = multivariable_task(electron_x, electron_y)
        return 1

    # list-type inputs

    list_workflow.build_graph([1, 2, 3])
    serialized_args = [ct.TransportableObject(i) for i in [1, 2, 3]]
    tg = list_workflow.transport_graph
    # Nodes 0=task, 1=:electron_list:, 2=1, 3=2, 4=3
    tg.set_node_value(2, "output", ct.TransportableObject(1))
    tg.set_node_value(3, "output", ct.TransportableObject(2))
    tg.set_node_value(4, "output", ct.TransportableObject(3))

    result_object = Result(lattice=list_workflow, results_dir="/tmp", dispatch_id="asdf")
    task_inputs = _get_task_inputs(1, tg.get_node_value(1, "name"), result_object)

    expected_inputs = {"args": [], "kwargs": {"x": ct.TransportableObject(serialized_args)}}

    assert (
        task_inputs["kwargs"]["x"].get_deserialized()
        == expected_inputs["kwargs"]["x"].get_deserialized()
    )

    # dict-type inputs

    dict_workflow.build_graph({"a": 1, "b": 2})
    serialized_args = {"a": ct.TransportableObject(1), "b": ct.TransportableObject(2)}
    tg = dict_workflow.transport_graph
    # Nodes 0=task, 1=:electron_dict:, 2=1, 3=2
    tg.set_node_value(2, "output", ct.TransportableObject(1))
    tg.set_node_value(3, "output", ct.TransportableObject(2))

    result_object = Result(lattice=dict_workflow, results_dir="/tmp", dispatch_id="asdf")
    task_inputs = _get_task_inputs(1, tg.get_node_value(1, "name"), result_object)
    expected_inputs = {"args": [], "kwargs": {"x": ct.TransportableObject(serialized_args)}}

    assert (
        task_inputs["kwargs"]["x"].get_deserialized()
        == expected_inputs["kwargs"]["x"].get_deserialized()
    )

    # Check arg order
    multivar_workflow.build_graph(1, 2)
    received_lattice = Lattice.deserialize_from_json(multivar_workflow.serialize_to_json())
    result_object = Result(lattice=received_lattice, results_dir="/tmp", dispatch_id="asdf")
    tg = received_lattice.transport_graph

    assert list(tg._graph.nodes) == [0, 1, 2, 3, 4, 5, 6, 7]
    tg.set_node_value(0, "output", ct.TransportableObject(1))
    tg.set_node_value(2, "output", ct.TransportableObject(2))

    task_inputs = _get_task_inputs(4, tg.get_node_value(4, "name"), result_object)

    input_args = [arg.get_deserialized() for arg in task_inputs["args"]]
    assert input_args == [1, 2]

    task_inputs = _get_task_inputs(5, tg.get_node_value(5, "name"), result_object)
    input_args = [arg.get_deserialized() for arg in task_inputs["args"]]
    assert input_args == [2, 1]

    task_inputs = _get_task_inputs(6, tg.get_node_value(6, "name"), result_object)
    input_args = [arg.get_deserialized() for arg in task_inputs["args"]]
    assert input_args == [2, 1]

    task_inputs = _get_task_inputs(7, tg.get_node_value(7, "name"), result_object)
    input_args = [arg.get_deserialized() for arg in task_inputs["args"]]
    assert input_args == [1, 2]


def test_gather_deps():
    """Test internal _gather_deps for assembling deps into call_before and
    call_after"""

    def square(x):
        return x * x

    @ct.electron(deps_bash=ct.DepsBash("ls -l"), call_after=[ct.DepsCall(square, [3])])
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph(5)

    received_workflow = Lattice.deserialize_from_json(workflow.serialize_to_json())
    result_object = Result(received_workflow, "/tmp", "asdf")

    before, after = _gather_deps(result_object, 0)
    assert len(before) == 1
    assert len(after) == 1


@pytest.mark.asyncio
async def test_update_failed_node(mocker):
    """Check that update_node_result correctly invokes _handle_failed_node"""

    tasks_queue = Queue()
    pending_deps = {}

    result_object = get_mock_result()
    mock_fail_handler = mocker.patch("covalent_dispatcher._core.execution._handle_failed_node")
    mock_upsert_lattice = mocker.patch("covalent_dispatcher._db.upsert._lattice_data")
    mock_update_node = mocker.patch("covalent_dispatcher._db.update._node")

    node_result = {"node_id": 0, "status": Result.FAILED}
    await _update_node_result(result_object, node_result, pending_deps, tasks_queue)

    mock_fail_handler.assert_called_once_with(
        result_object, node_result, pending_deps, tasks_queue
    )


@pytest.mark.asyncio
async def test_update_cancelled_node(mocker):
    """Check that update_node_result correctly invokes _handle_cancelled_node"""

    tasks_queue = Queue()
    pending_deps = {}

    result_object = get_mock_result()
    mock_cancel_handler = mocker.patch(
        "covalent_dispatcher._core.execution._handle_cancelled_node"
    )
    mock_upsert_lattice = mocker.patch("covalent_dispatcher._db.upsert._lattice_data")
    mock_update_node = mocker.patch("covalent_dispatcher._db.update._node")

    node_result = {"node_id": 0, "status": Result.CANCELLED}
    await _update_node_result(result_object, node_result, pending_deps, tasks_queue)

    mock_cancel_handler.assert_called_once_with(
        result_object, node_result, pending_deps, tasks_queue
    )


@pytest.mark.asyncio
async def test_update_completed_node(mocker):
    """Check that update_node_result correctly invokes _handle_completed_node"""

    tasks_queue = Queue()
    pending_deps = {}

    result_object = get_mock_result()
    mock_completed_handler = mocker.patch(
        "covalent_dispatcher._core.execution._handle_completed_node"
    )
    mock_upsert_lattice = mocker.patch("covalent_dispatcher._db.upsert._lattice_data")
    mock_update_node = mocker.patch("covalent_dispatcher._db.update._node")

    node_result = {"node_id": 0, "status": Result.COMPLETED}
    await _update_node_result(result_object, node_result, pending_deps, tasks_queue)

    mock_completed_handler.assert_called_once_with(
        result_object, node_result, pending_deps, tasks_queue
    )


@pytest.mark.asyncio
async def test_handle_completed_node(mocker):
    """Unit test for completed node handler"""
    tasks_queue = Queue()
    pending_deps = {}

    result_object = get_mock_result()

    # tg edges are (1, 0), (0, 2)
    pending_deps[0] = 1
    pending_deps[1] = 0
    pending_deps[2] = 1

    mock_upsert_lattice = mocker.patch("covalent_dispatcher._db.upsert._lattice_data")

    node_result = {"node_id": 1, "status": Result.COMPLETED}

    await _handle_completed_node(result_object, node_result, pending_deps, tasks_queue)

    assert await asyncio.wait_for(tasks_queue.get(), timeout=1) == 0
    assert pending_deps == {0: 0, 1: 0, 2: 1}


@pytest.mark.asyncio
async def test_handle_failed_node(mocker):
    """Unit test for failed node handler"""
    tasks_queue = Queue()
    pending_deps = {}

    result_object = get_mock_result()

    # tg edges are (1, 0), (0, 2)
    pending_deps[0] = 1
    pending_deps[1] = 0
    pending_deps[2] = 1

    mock_upsert_lattice = mocker.patch("covalent_dispatcher._db.upsert._lattice_data")
    mock_get_node_name = mocker.patch("covalent._results_manager.result.Result._get_node_name")

    mock_get_node_error = mocker.patch("covalent._results_manager.result.Result._get_node_error")

    node_result = {"node_id": 1, "status": Result.FAILED}

    await _handle_failed_node(result_object, node_result, pending_deps, tasks_queue)

    assert await asyncio.wait_for(tasks_queue.get(), timeout=1) == -1
    assert pending_deps == {0: 1, 1: 0, 2: 1}
    assert result_object.status == Result.FAILED
    mock_get_node_name.assert_called_once()
    mock_get_node_error.assert_called_once()


@pytest.mark.asyncio
async def test_handle_cancelled_node(mocker):
    """Unit test for cancelled node handler"""
    tasks_queue = Queue()
    pending_deps = {}

    result_object = get_mock_result()

    # tg edges are (1, 0), (0, 2)
    pending_deps[0] = 1
    pending_deps[1] = 0
    pending_deps[2] = 1

    mock_upsert_lattice = mocker.patch("covalent_dispatcher._db.upsert._lattice_data")

    node_result = {"node_id": 1, "status": Result.CANCELLED}

    await _handle_cancelled_node(result_object, node_result, pending_deps, tasks_queue)

    assert await asyncio.wait_for(tasks_queue.get(), timeout=1) == -1
    assert pending_deps == {0: 1, 1: 0, 2: 1}
    assert result_object.status == Result.CANCELLED


@pytest.mark.asyncio
async def test_initialize_deps_and_queue(mocker):
    """Test internal function for initializing tasks_queue and pending_deps"""
    tasks_queue = Queue()
    pending_deps = {}

    result_object = get_mock_result()
    num_tasks = await _initialize_deps_and_queue(result_object, tasks_queue, pending_deps)

    assert await asyncio.wait_for(tasks_queue.get(), timeout=1) == 1
    assert pending_deps == {0: 1, 1: 0, 2: 1}
    assert num_tasks == len(result_object.lattice.transport_graph._graph.nodes)


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
    mocker.patch("covalent_dispatcher._core.execution.update_lattices_data")
    mocker.patch("covalent_dispatcher._core.execution.write_lattice_error")

    update.persist(result_object)
    result_object = await run_workflow(result_object)

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
    mocker.patch("covalent_dispatcher._core.execution.update_lattices_data")
    mocker.patch("covalent_dispatcher._core.execution.write_lattice_error")

    update.persist(result_object)

    result_object = await run_workflow(result_object)

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
    update.persist(result_object)

    mock_to_deserialize = mocker.patch("covalent.TransportableObject.get_deserialized")

    result_object = await run_workflow(result_object)

    mock_to_deserialize.assert_not_called()
    assert result_object.status == Result.COMPLETED


@pytest.mark.asyncio
async def test_run_workflow_with_client_side_postprocess(test_db, mocker):
    """Check that run_workflow handles "client" workflow_executor for
    postprocessing"""

    import asyncio

    dispatch_id = "asdf"
    result_object = get_mock_result()
    result_object.lattice.set_metadata("workflow_executor", "client")
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)

    update.persist(result_object)

    result_object = await run_workflow(result_object)
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

    update.persist(result_object)

    def failing_workflow(x):
        assert False

    result_object.lattice.set_metadata("workflow_executor", "bogus")
    result_object = await run_workflow(result_object)

    assert result_object.status == Result.POSTPROCESSING_FAILED

    result_object.lattice.workflow_function = ct.TransportableObject(failing_workflow)
    result_object.lattice.set_metadata("workflow_executor", "local")

    result_object = await run_workflow(result_object)

    assert result_object.status == Result.POSTPROCESSING_FAILED


def test_build_sublattice_graph():
    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    json_lattice = _build_sublattice_graph(workflow, 1)
    lattice = Lattice.deserialize_from_json(json_lattice)

    assert list(lattice.transport_graph._graph.nodes) == [0, 1]


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
        "covalent_dispatcher._core.execution.get_sublattice_electron_id", return_value=1
    )
    mock_dispatch_sync = mocker.patch(
        "covalent_dispatcher._core.execution._dispatch_sync_sublattice",
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
        "covalent_dispatcher._core.execution._dispatch_sync_sublattice",
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
        "covalent_dispatcher._core.execution._dispatch_sync_sublattice", return_value=None
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


@pytest.mark.asyncio
async def test_run_task_executor_exception_handling(mocker):
    """Test that exceptions from initializing executors are caught"""

    result_object = get_mock_result()
    inputs = {"args": [], "kwargs": {}}
    mock_get_executor = mocker.patch(
        "covalent_dispatcher._core.execution._executor_manager.get_executor",
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
        node_name=sublattice_prefix,
        workflow_executor=["local", {}],
    )

    assert node_result["status"] == Result.FAILED
