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
    _plan_workflow,
    _post_process,
    _run_task,
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
        return task(x)

    pipeline.build_graph(x="absolute")

    return Result(
        lattice=pipeline,
        results_dir=pipeline.metadata["results_dir"],
    )


def test_plan_workflow():
    """Test workflow planning method."""

    mock_result = get_mock_result()
    mock_result.lattice.metadata["schedule"] = True
    _plan_workflow(result_object=mock_result)

    # Updated transport graph post planning
    updated_tg = pickle.loads(mock_result.lattice.transport_graph.serialize(metadata_only=True))

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

    order = [
        i for i in range(len(compute_energy.transport_graph.get_internal_graph_copy().nodes()))
    ]

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

    execution_result = _post_process(compute_energy, encoded_node_outputs, order)

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
    def list_task(arg: []):
        return len(arg)

    @ct.electron
    def dict_task(arg: dict):
        return len(arg)

    @ct.lattice
    def list_workflow(arg):
        return list_task(arg)

    @ct.lattice
    def dict_workflow(arg):
        return dict_task(arg)

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


def test_run_task(mocker, sublattice_workflow):
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

    _run_task(
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
