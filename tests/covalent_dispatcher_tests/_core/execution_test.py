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
from threading import Lock
from typing import Dict, List

import cloudpickle as pickle
import pytest

import covalent as ct
from covalent._data_store.datastore import DataStore
from covalent._results_manager import Result
from covalent._results_manager.utils import _db_path
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.execution import (
    _gather_deps,
    _get_task_inputs,
    _handle_cancelled_node,
    _handle_completed_node,
    _handle_failed_node,
    _initialize_deps_and_queue,
    _plan_workflow,
    _post_process,
    _postprocess_workflow,
    _run_planned_workflow,
    _run_task,
    _update_node_result,
    generate_node_result,
    run_workflow,
)

TEST_RESULTS_DIR = "/tmp/results"


@ct.electron
def a(x):
    return x, x**2


@ct.lattice
def p(x):
    result, b = a(x=x)
    for _ in range(1):
        result, b = a(x=result)
    return b, result


@pytest.fixture
def sublattice_workflow():
    @ct.electron
    @ct.lattice
    def sublattice(x):
        res = a(x)
        return res

    @ct.lattice
    def parent_workflow(x):
        res = sublattice(x)
        return res

    parent_workflow.build_graph(x=1)
    return parent_workflow


def get_mock_result() -> Result:
    """Construct a mock result object corresponding to a lattice."""

    import sys

    @ct.electron
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


def test_result_post_process():
    """Test client-side post-processing of results."""

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

    compute_energy = Lattice.deserialize_from_json(compute_energy.serialize_to_json())

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

    res = Result(compute_energy, compute_energy.metadata["results_dir"])
    res._initialize_nodes()

    for i, v in enumerate(encoded_node_outputs.values()):
        compute_energy.transport_graph.set_node_value(i, "output", v)

    res._status = Result.PENDING_POSTPROCESSING
    res._dispatch_id = "MOCK"
    res.persist(DataStore(db_URL=f"sqlite+pysqlite:///{_db_path()}", initialize_db=True))
    execution_result = res.post_process()

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
async def test_run_task(mocker, sublattice_workflow):
    """Note: This is not a full unit test for the _run_task method. Rather, this is intended to test the diff introduced to write the sublattice electron id in the Database."""

    # class MockResult:
    #     dispatch_id = "test"

    # def mock_func():
    #     return MockResult()
    # class MockSerializedCallable:
    #     def get_deserialized(self):
    #         return mock_func

    from concurrent.futures import ThreadPoolExecutor

    tasks_pool = ThreadPoolExecutor()

    write_sublattice_electron_id_mock = mocker.patch(
        "covalent_dispatcher._core.execution.write_sublattice_electron_id"
    )
    ct.dispatch(sublattice_workflow)(1)

    await _run_task(
        node_id=1,
        dispatch_id="parent_dispatch_id",
        results_dir="/tmp",
        inputs={"args": [], "kwargs": {"x": ct.TransportableObject(1)}},
        serialized_callable=sublattice_workflow.transport_graph.get_node_value(
            0,
            "function",
        ),
        selected_executor=["local", {}],
        call_before=[],
        call_after=[],
        node_name=":sublattice:sublattice",
        tasks_pool=tasks_pool,
        workflow_executor=["local", {}],
    )
    write_sublattice_electron_id_mock.assert_called_once()


@pytest.mark.asyncio
async def test_update_failed_node(mocker):
    """Check that update_node_result correctly invokes _handle_failed_node"""

    lock = Lock()
    tasks_queue = Queue()
    pending_deps = {}

    result_object = get_mock_result()
    mock_fail_handler = mocker.patch("covalent_dispatcher._core.execution._handle_failed_node")
    mock_upsert_lattice = mocker.patch(
        "covalent._results_manager.result.Result.upsert_lattice_data"
    )
    mock_update_node = mocker.patch("covalent._results_manager.result.Result._update_node")

    node_result = {"node_id": 0, "status": Result.FAILED}
    await _update_node_result(lock, result_object, node_result, pending_deps, tasks_queue)

    mock_fail_handler.assert_called_once_with(
        result_object, node_result, pending_deps, tasks_queue
    )


@pytest.mark.asyncio
async def test_update_cancelled_node(mocker):
    """Check that update_node_result correctly invokes _handle_cancelled_node"""

    lock = Lock()
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
    await _update_node_result(lock, result_object, node_result, pending_deps, tasks_queue)

    mock_cancel_handler.assert_called_once_with(
        result_object, node_result, pending_deps, tasks_queue
    )


@pytest.mark.asyncio
async def test_update_completed_node(mocker):
    """Check that update_node_result correctly invokes _handle_completed_node"""

    lock = Lock()
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
    await _update_node_result(lock, result_object, node_result, pending_deps, tasks_queue)

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


def test_run_workflow_with_failing_nonleaf(mocker):
    """Test running workflow with a failing intermediate node"""

    @ct.electron
    def failing_task(x):
        assert False
        return x

    @ct.lattice
    def workflow(x):
        res1 = failing_task(x)
        res2 = failing_task(res1)
        return res2

    from concurrent.futures import ThreadPoolExecutor

    from covalent._workflow.lattice import Lattice
    from covalent_dispatcher._db.dispatchdb import DispatchDB

    workflow.build_graph(5)

    json_lattice = workflow.serialize_to_json()
    dispatch_id = "asdf"
    tasks_pool = ThreadPoolExecutor()
    lattice = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lattice, lattice.metadata["results_dir"])
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    DispatchDB().save_db(result_object)

    result_object = run_workflow(result_object, tasks_pool)

    assert result_object.status == Result.FAILED


def test_run_workflow_with_failing_leaf(mocker):
    """Test running workflow with a failing leaf node"""

    @ct.electron
    def failing_task(x):
        assert False
        return x

    @ct.lattice
    def workflow(x):
        res1 = failing_task(x)
        return res1

    from concurrent.futures import ThreadPoolExecutor

    from covalent._workflow.lattice import Lattice
    from covalent_dispatcher._db.dispatchdb import DispatchDB

    workflow.build_graph(5)

    json_lattice = workflow.serialize_to_json()
    dispatch_id = "asdf"
    tasks_pool = ThreadPoolExecutor()
    lattice = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lattice, lattice.metadata["results_dir"])
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    DispatchDB().save_db(result_object)

    result_object = run_workflow(result_object, tasks_pool)

    assert result_object.status == Result.FAILED


def test_run_workflow_does_not_deserialize(mocker):
    """Check that dispatcher does not deserialize user data when using
    out-of-process `workflow_executor`"""

    from concurrent.futures import ThreadPoolExecutor

    from covalent._workflow.lattice import Lattice
    from covalent_dispatcher._db.dispatchdb import DispatchDB

    @ct.electron(executor="dask")
    def task(x):
        return x

    @ct.lattice(executor="dask", workflow_executor="dask")
    def workflow(x):
        # Exercise both sublatticing and postprocessing
        sublattice_task = ct.lattice(task, workflow_executor="dask")
        res1 = ct.electron(sublattice_task(x), executor="dask")
        return res1

    workflow.build_graph(5)

    json_lattice = workflow.serialize_to_json()
    dispatch_id = "asdf"
    tasks_pool = ThreadPoolExecutor()
    lattice = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lattice, lattice.metadata["results_dir"])
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    DispatchDB().save_db(result_object)

    mock_to_deserialize = mocker.patch("covalent.TransportableObject.get_deserialized")

    result_object = run_workflow(result_object, tasks_pool)

    mock_to_deserialize.assert_not_called()
    assert result_object.status == Result.COMPLETED


def test_run_workflow_with_client_side_postprocess():
    """Check that run_workflow handles "client" workflow_executor for
    postprocessing"""

    from concurrent.futures import ThreadPoolExecutor

    from covalent._workflow.lattice import Lattice
    from covalent_dispatcher._db.dispatchdb import DispatchDB

    dispatch_id = "asdf"
    tasks_pool = ThreadPoolExecutor()
    result_object = get_mock_result()
    result_object.lattice.set_metadata("workflow_executor", "client")
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    DispatchDB().save_db(result_object)

    result_object = run_workflow(result_object, tasks_pool)
    assert result_object.status == Result.PENDING_POSTPROCESSING


def test_run_workflow_with_failed_postprocess():
    """Check that run_workflow handles postprocessing failures"""

    from concurrent.futures import ThreadPoolExecutor

    from covalent._workflow.lattice import Lattice
    from covalent_dispatcher._db.dispatchdb import DispatchDB

    dispatch_id = "asdf"
    tasks_pool = ThreadPoolExecutor()
    result_object = get_mock_result()
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    DispatchDB().save_db(result_object)

    def failing_workflow(x):
        assert False
        return 1

    result_object.lattice.set_metadata("workflow_executor", "bogus")
    result_object = run_workflow(result_object, tasks_pool)

    assert result_object.status == Result.POSTPROCESSING_FAILED

    result_object.lattice.workflow_function = ct.TransportableObject(failing_workflow)
    result_object.lattice.set_metadata("workflow_executor", "dask")

    result_object = run_workflow(result_object, tasks_pool)

    assert result_object.status == Result.POSTPROCESSING_FAILED
