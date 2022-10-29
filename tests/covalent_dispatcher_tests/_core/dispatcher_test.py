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


from asyncio import Queue
from typing import Dict, List

import cloudpickle as pickle
import pytest

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.dispatcher import (
    _build_sublattice_graph,
    _get_abstract_task_inputs,
    _handle_cancelled_node,
    _handle_completed_node,
    _handle_failed_node,
    _initialize_deps_and_queue,
    _plan_workflow,
    _post_process,
    run_dispatch,
)
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


def test_get_abstract_task_inputs():
    """Test _get_abstract_task_inputs for both dicts and list parameter types"""

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

    # Nodes 0=task, 1=:electron_list:, 2=1, 3=2, 4=3
    list_workflow.build_graph([1, 2, 3])
    abstract_args = [2, 3, 4]
    tg = list_workflow.transport_graph

    result_object = Result(lattice=list_workflow, results_dir="/tmp", dispatch_id="asdf")
    abs_task_inputs = _get_abstract_task_inputs(1, tg.get_node_value(1, "name"), result_object)

    expected_inputs = {"args": abstract_args, "kwargs": {}}

    assert abs_task_inputs == expected_inputs

    # dict-type inputs

    # Nodes 0=task, 1=:electron_dict:, 2=1, 3=2
    dict_workflow.build_graph({"a": 1, "b": 2})
    abstract_args = {"a": 2, "b": 3}
    tg = dict_workflow.transport_graph

    result_object = Result(lattice=dict_workflow, results_dir="/tmp", dispatch_id="asdf")
    task_inputs = _get_abstract_task_inputs(1, tg.get_node_value(1, "name"), result_object)
    expected_inputs = {"args": [], "kwargs": abstract_args}

    assert task_inputs == expected_inputs

    # Check arg order
    multivar_workflow.build_graph(1, 2)
    received_lattice = Lattice.deserialize_from_json(multivar_workflow.serialize_to_json())
    result_object = Result(lattice=received_lattice, results_dir="/tmp", dispatch_id="asdf")
    tg = received_lattice.transport_graph

    assert list(tg._graph.nodes) == [0, 1, 2, 3, 4, 5, 6, 7]
    tg.set_node_value(0, "output", ct.TransportableObject(1))
    tg.set_node_value(2, "output", ct.TransportableObject(2))

    task_inputs = _get_abstract_task_inputs(4, tg.get_node_value(4, "name"), result_object)
    assert task_inputs["args"] == [0, 2]

    task_inputs = _get_abstract_task_inputs(5, tg.get_node_value(5, "name"), result_object)
    assert task_inputs["args"] == [2, 0]

    task_inputs = _get_abstract_task_inputs(6, tg.get_node_value(6, "name"), result_object)
    assert task_inputs["args"] == [2, 0]

    task_inputs = _get_abstract_task_inputs(7, tg.get_node_value(7, "name"), result_object)
    assert task_inputs["args"] == [0, 2]


@pytest.mark.asyncio
async def test_handle_completed_node(mocker):
    """Unit test for completed node handler"""
    status_queue = Queue()
    pending_deps = {}

    result_object = get_mock_result()

    # tg edges are (1, 0), (0, 2)
    pending_deps[0] = 1
    pending_deps[1] = 0
    pending_deps[2] = 1

    mock_upsert_lattice = mocker.patch("covalent_dispatcher._db.upsert._lattice_data")

    node_result = {"node_id": 1, "status": Result.COMPLETED}

    next_nodes = await _handle_completed_node(result_object, 1, pending_deps)
    assert next_nodes == [0]
    assert pending_deps == {0: 0, 1: 0, 2: 1}


@pytest.mark.asyncio
async def test_handle_failed_node(mocker):
    """Unit test for failed node handler"""
    status_queue = Queue()
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

    await _handle_failed_node(result_object, 1)

    assert pending_deps == {0: 1, 1: 0, 2: 1}
    assert result_object.status == Result.FAILED
    mock_get_node_name.assert_called_once()
    mock_get_node_error.assert_called_once()


@pytest.mark.asyncio
async def test_handle_cancelled_node(mocker):
    """Unit test for cancelled node handler"""
    status_queue = Queue()
    pending_deps = {}

    result_object = get_mock_result()

    # tg edges are (1, 0), (0, 2)
    pending_deps[0] = 1
    pending_deps[1] = 0
    pending_deps[2] = 1

    mock_upsert_lattice = mocker.patch("covalent_dispatcher._db.upsert._lattice_data")

    node_result = {"node_id": 1, "status": Result.CANCELLED}

    await _handle_cancelled_node(result_object, 1)

    assert pending_deps == {0: 1, 1: 0, 2: 1}
    assert result_object.status == Result.CANCELLED


@pytest.mark.asyncio
async def test_initialize_deps_and_queue(mocker):
    """Test internal function for initializing status_queue and pending_deps"""
    status_queue = Queue()
    pending_deps = {}

    result_object = get_mock_result()
    num_tasks, initial_nodes, pending_deps = await _initialize_deps_and_queue(result_object)

    assert initial_nodes == [1]
    assert pending_deps == {0: 1, 1: 0, 2: 1}
    assert num_tasks == len(result_object.lattice.transport_graph._graph.nodes)


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
async def test_run_dispatch(mocker):
    res = get_mock_result()
    mocker.patch(
        "covalent_dispatcher._core.dispatcher.resultsvc.get_result_object", return_value=res
    )
    mock_run = mocker.patch("covalent_dispatcher._core.dispatcher.run_workflow")
    run_dispatch(res.dispatch_id)
    mock_run.assert_called_with(res)
