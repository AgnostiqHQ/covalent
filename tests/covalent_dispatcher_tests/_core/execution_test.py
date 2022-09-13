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
from unittest.mock import AsyncMock, MagicMock

import cloudpickle as pickle
import pytest

import covalent as ct
from covalent._data_store.datastore import DataStore
from covalent._results_manager import Result
from covalent._shared_files.defaults import sublattice_prefix
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.execution import (
    ExecutorCache,
    _build_sublattice_graph,
    _dispatch_sync_sublattice,
    _gather_deps,
    _get_executor_instance,
    _get_task_inputs,
    _handle_cancelled_node,
    _handle_completed_node,
    _handle_failed_node,
    _initialize_deps_and_queue,
    _plan_workflow,
    _post_process,
    _run_task,
    _update_node_result,
    run_workflow,
)

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
    mock_upsert_lattice = mocker.patch(
        "covalent._results_manager.result.Result.upsert_lattice_data"
    )
    mock_update_node = mocker.patch("covalent._results_manager.result.Result._update_node")

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
    mock_upsert_lattice = mocker.patch(
        "covalent._results_manager.result.Result.upsert_lattice_data"
    )
    mock_update_node = mocker.patch("covalent._results_manager.result.Result._update_node")

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
    mock_upsert_lattice = mocker.patch(
        "covalent._results_manager.result.Result.upsert_lattice_data"
    )
    mock_update_node = mocker.patch("covalent._results_manager.result.Result._update_node")

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

    mock_upsert_lattice = mocker.patch(
        "covalent._results_manager.result.Result.upsert_lattice_data"
    )

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

    mock_upsert_lattice = mocker.patch(
        "covalent._results_manager.result.Result.upsert_lattice_data"
    )
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

    mock_upsert_lattice = mocker.patch(
        "covalent._results_manager.result.Result.upsert_lattice_data"
    )

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
    mocker.patch("covalent._results_manager.result.Result.upsert_lattice_data")
    mocker.patch("covalent._results_manager.result.Result.upsert_electron_data")
    mocker.patch("covalent._results_manager.result.Result.persist")
    mocker.patch(
        "covalent._results_manager.result.Result._get_node_name", return_value="failing_task"
    )
    mocker.patch(
        "covalent._results_manager.result.Result._get_node_error", return_value="AssertionError"
    )
    mocker.patch("covalent_dispatcher._core.execution.update_lattices_data")
    mocker.patch("covalent_dispatcher._core.execution.write_lattice_error")

    result_object.persist()
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

    mocker.patch("covalent._results_manager.result.Result.upsert_lattice_data")
    mocker.patch("covalent._results_manager.result.Result.upsert_electron_data")
    mocker.patch("covalent._results_manager.result.Result.persist")
    mocker.patch(
        "covalent._results_manager.result.Result._get_node_name", return_value="failing_task"
    )
    mocker.patch(
        "covalent._results_manager.result.Result._get_node_error", return_value="AssertionError"
    )
    mocker.patch("covalent_dispatcher._core.execution.update_lattices_data")
    mocker.patch("covalent_dispatcher._core.execution.write_lattice_error")

    result_object.persist()

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

    mocker.patch("covalent._data_store.datastore.DataStore.factory", return_value=test_db)
    result_object.persist()

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

    mocker.patch("covalent._results_manager.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent._results_manager.result.workflow_db", test_db)

    result_object.persist()

    result_object = await run_workflow(result_object)
    assert result_object.status == Result.PENDING_POSTPROCESSING


@pytest.mark.asyncio
async def test_run_workflow_with_failed_postprocess(test_db, mocker):
    """Check that run_workflow handles postprocessing failures"""

    dispatch_id = "asdf"
    result_object = get_mock_result()
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    mocker.patch("covalent._results_manager.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent._results_manager.result.workflow_db", test_db)

    result_object.persist()

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
async def test_dispatch_sync_sublattice(mocker):

    from covalent.executor import LocalExecutor

    le = LocalExecutor()
    executor_cache = ExecutorCache()
    executor_cache.id_instance_map[le.instance_id] = le
    executor_cache.tasks_per_instance[le.instance_id] = 1

    mocker.patch("covalent._data_store.datastore.DataStore.factory", return_value=test_db)

    @ct.electron(executor="local")
    def task(x):
        return x

    @ct.lattice(executor="local", workflow_executor="local")
    def sub_workflow(x):
        return task(x)

    mocker.patch("covalent._results_manager.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent._results_manager.result.workflow_db", test_db)

    result_object = get_mock_result()

    serialized_callable = ct.TransportableObject(sub_workflow)
    inputs = {"args": [ct.TransportableObject(2)], "kwargs": {}}

    sub_result = await _dispatch_sync_sublattice(
        parent_result_object=result_object,
        parent_electron_id=1,
        inputs=inputs,
        serialized_callable=serialized_callable,
        workflow_executor=[le.short_name(), le.to_dict()],
        executor_cache=executor_cache,
    )
    assert sub_result.result == 2

    # Check handling of invalid workflow executors

    try:
        sub_result = await _dispatch_sync_sublattice(
            parent_result_object=result_object,
            parent_electron_id=1,
            inputs=inputs,
            serialized_callable=serialized_callable,
            workflow_executor=["client", {}],
            executor_cache=executor_cache,
        )
        assert False

    except RuntimeError:
        pass

    try:
        bad_short_name = "fake_executor"
        bad_object_dict = {
            "type": "FakeExecutor",
            "short_name": "fake_executor",
            "attributes": {"instance_id": -1},
        }
        executor_cache.id_instance_map[-1] = None
        sub_result = await _dispatch_sync_sublattice(
            parent_result_object=result_object,
            parent_electron_id=1,
            inputs=inputs,
            serialized_callable=serialized_callable,
            workflow_executor=["fake_executor", bad_object_dict],
            executor_cache=executor_cache,
        )
        assert False

    except ValueError:
        pass


@pytest.mark.asyncio
async def test_run_task_sublattice_handling(test_db, mocker):

    from covalent.executor import LocalExecutor

    le = LocalExecutor()

    executor_cache = ExecutorCache()
    executor_cache.id_instance_map[le.instance_id] = le
    executor_cache.tasks_per_instance[le.instance_id] = 1

    result_object = get_mock_result()
    sub_result_object = get_mock_result()
    sub_result_object._dispatch_id = "sublattice_workflow"
    sub_result_object._result = ct.TransportableObject(5)
    sub_result_object._status = Result.COMPLETED

    mocker.patch("covalent._results_manager.write_result_to_db.workflow_db", test_db)
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
        selected_executor=[le.short_name(), le.to_dict()],
        call_before=[],
        call_after=[],
        node_name=sublattice_prefix,
        workflow_executor=[le.short_name(), le.to_dict()],
        executor_cache=executor_cache,
        unplanned_task=False,
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
        selected_executor=[le.short_name(), le.to_dict()],
        call_before=[],
        call_after=[],
        node_name=sublattice_prefix,
        workflow_executor=[le.short_name(), le.to_dict()],
        executor_cache=executor_cache,
        unplanned_task=False,
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
        selected_executor=[le.short_name(), le.to_dict()],
        call_before=[],
        call_after=[],
        node_name=sublattice_prefix,
        workflow_executor=[le.short_name(), le.to_dict()],
        executor_cache=executor_cache,
        unplanned_task=False,
    )

    assert node_result["status"] == Result.FAILED


def test_executor_cache_initialize():
    """Test ExecuterCache initialize correctly counts the tasks assigned
    to each cached executor"""

    from covalent._workflow.lattice import Lattice
    from covalent.executor import LocalExecutor

    le1 = LocalExecutor().get_shared_instance()
    le2 = LocalExecutor().get_shared_instance()
    le3 = LocalExecutor()

    id_1 = le1.instance_id
    id_2 = le2.instance_id

    @ct.electron(executor=le1)
    def task_1(x):
        return x

    @ct.electron(executor=le2)
    def task_2(x):
        return x

    @ct.electron(executor=le2)
    def task_3(x):
        return x

    @ct.electron(executor="local")
    def task_4(x):
        return x

    @ct.lattice(workflow_executor="local")
    def workflow_1(x):
        res1 = task_1(x)
        res2 = task_2(res1)
        res3 = task_3(res2)
        res4 = task_4(res3)
        return res4

    @ct.lattice(workflow_executor=le2)
    def workflow_2(x):
        res1 = task_1(x)
        res2 = task_2(res1)
        res3 = task_3(res2)
        res4 = task_4(res3)
        return res4

    @ct.lattice(workflow_executor=le3)
    def workflow_3(x):
        res1 = task_1(x)
        res2 = task_2(res1)
        res3 = task_3(res2)
        res4 = task_4(res3)
        return res4

    @ct.lattice(workflow_executor=le2)
    def workflow_4(x):
        return task_1(x)

    workflow_1.build_graph(5)
    received_lattice = Lattice.deserialize_from_json(workflow_1.serialize_to_json())

    result_object = Result(received_lattice, "/tmp", "asdf")

    cache = ExecutorCache()
    cache.initialize_from_result_object(result_object)

    tg = received_lattice.transport_graph

    task4_eid = tg._graph.nodes[4]["metadata"]["executor_data"]["attributes"]["instance_id"]
    workflow_eid = received_lattice.metadata["workflow_executor_data"]["attributes"]["instance_id"]
    assert id_1 in cache.id_instance_map.keys()
    assert id_2 in cache.id_instance_map.keys()
    assert task4_eid in cache.id_instance_map.keys()
    assert workflow_eid in cache.id_instance_map.keys()
    assert len(cache.id_instance_map.keys()) == 4
    assert cache.tasks_per_instance[id_1] == 1
    assert cache.tasks_per_instance[id_2] == 2
    assert cache.tasks_per_instance[task4_eid] == 1
    assert cache.tasks_per_instance[workflow_eid] == 1

    # Test using shared workflow executor instance
    workflow_2.build_graph(5)
    received_lattice = Lattice.deserialize_from_json(workflow_2.serialize_to_json())

    result_object = Result(received_lattice, "/tmp", "asdf")

    cache = ExecutorCache()
    cache.initialize_from_result_object(result_object)

    assert cache.tasks_per_instance[id_1] == 1
    assert cache.tasks_per_instance[id_2] == 3

    # Test using exclusive workflow executor instance
    workflow_3.build_graph(5)
    received_lattice = Lattice.deserialize_from_json(workflow_3.serialize_to_json())
    result_object = Result(received_lattice, "/tmp", "asdf")

    cache = ExecutorCache()
    cache.initialize_from_result_object(result_object)

    assert cache.tasks_per_instance[id_1] == 1
    assert cache.tasks_per_instance[id_2] == 2

    # Test using workflow executor instance not shared by any other tasks
    workflow_4.build_graph(5)
    received_lattice = Lattice.deserialize_from_json(workflow_4.serialize_to_json())

    result_object = Result(received_lattice, "/tmp", "asdf")

    cache = ExecutorCache()
    cache.initialize_from_result_object(result_object)

    assert cache.tasks_per_instance[id_1] == 1
    assert cache.tasks_per_instance[id_2] == 1


@pytest.mark.asyncio
async def test_executor_cache_finalize():
    """Test `ExecutorCache.finalize()`"""

    from covalent.executor import DaskExecutor, LocalExecutor

    le = LocalExecutor().get_shared_instance()
    de = DaskExecutor("tcp://127.0.0.1:30000").get_shared_instance()

    le.teardown = MagicMock()
    de.teardown = AsyncMock()

    cache = ExecutorCache()
    cache.id_instance_map[le.instance_id] = le
    cache.id_instance_map[de.instance_id] = de

    await cache.finalize_executors()

    le.teardown.assert_called_once()
    de.teardown.assert_awaited_once()


def test_get_executor_instance():
    """Test _get_executor_instance"""

    from covalent._workflow.lattice import Lattice
    from covalent.executor import LocalExecutor

    le = LocalExecutor()
    le_shared_instance = le.get_shared_instance()

    @ct.electron(executor="local")
    def task_1(x):
        return x

    @ct.electron(executor=le)
    def task_2(x):
        return x

    @ct.electron(executor=le_shared_instance)
    def task_3(x):
        return x

    @ct.electron(executor=le_shared_instance)
    def task_4(x):
        return x

    @ct.lattice(workflow_executor="local")
    def workflow_1(x):
        res1 = task_1(x)
        res2 = task_2(res1)
        res3 = task_3(res2)
        res4 = task_4(res3)
        return res1 + res2 + res3 + res4

    workflow_1.build_graph(5)
    received_lattice = Lattice.deserialize_from_json(workflow_1.serialize_to_json())

    result_object = Result(received_lattice, "/tmp", "asdf")

    cache = ExecutorCache()
    cache.initialize_from_result_object(result_object)
    tg = result_object.lattice.transport_graph

    # short name
    node_id = 0
    node_name = tg.get_node_value(node_id, "name")
    executor = tg.get_node_value(node_id, "metadata")["executor"]
    executor_data = tg.get_node_value(node_id, "metadata")["executor_data"]
    selected_executor = [executor, executor_data]

    executor_instance = _get_executor_instance(
        node_id=node_id,
        dispatch_id="asdf",
        node_name=node_name,
        selected_executor=selected_executor,
        executor_cache=cache,
        unplanned_task=False,
    )

    assert executor_instance.short_name() == "local"

    # throwaway instance -- don't cache
    node_id = 2
    node_name = tg.get_node_value(node_id, "name")
    executor = tg.get_node_value(node_id, "metadata")["executor"]
    executor_data = tg.get_node_value(node_id, "metadata")["executor_data"]
    assert executor_data["attributes"]["shared"] is False
    selected_executor = [executor, executor_data]

    executor_instance = _get_executor_instance(
        node_id=node_id,
        dispatch_id="asdf",
        node_name=node_name,
        selected_executor=selected_executor,
        executor_cache=cache,
        unplanned_task=False,
    )

    assert executor_instance.short_name() == "local"

    # shared instance -- to cache
    node_id = 3
    node_name = tg.get_node_value(node_id, "name")
    executor = tg.get_node_value(node_id, "metadata")["executor"]
    executor_data = tg.get_node_value(node_id, "metadata")["executor_data"]
    assert executor_data["attributes"]["shared"] is True
    selected_executor = [executor, executor_data]

    shared_instance = _get_executor_instance(
        node_id=node_id,
        dispatch_id="asdf",
        node_name=node_name,
        selected_executor=selected_executor,
        executor_cache=cache,
        unplanned_task=False,
    )

    exec_id = shared_instance.instance_id
    assert shared_instance.short_name() == "local"
    assert shared_instance.is_shared_instance()
    assert cache.id_instance_map[exec_id] == shared_instance
    assert shared_instance.tasks_left == cache.tasks_per_instance[exec_id]

    # shared instance -- retrieve from cache
    node_id = 4
    node_name = tg.get_node_value(node_id, "name")
    executor = tg.get_node_value(node_id, "metadata")["executor"]
    executor_data = tg.get_node_value(node_id, "metadata")["executor_data"]
    selected_executor = [executor, executor_data]

    new_shared_instance = _get_executor_instance(
        node_id=node_id,
        dispatch_id="asdf",
        node_name=node_name,
        selected_executor=selected_executor,
        executor_cache=cache,
        unplanned_task=False,
    )

    assert new_shared_instance is shared_instance

    task_count = shared_instance.tasks_left

    # Test increment task count (for un-planned tasks)
    shared_instance = _get_executor_instance(
        node_id=node_id,
        dispatch_id="asdf",
        node_name=node_name,
        selected_executor=selected_executor,
        executor_cache=cache,
        unplanned_task=True,
    )

    task_count += 1
    assert task_count == shared_instance.tasks_left
