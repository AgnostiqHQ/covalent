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


import pytest

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.data_manager import get_result_object
from covalent_dispatcher._core.runner import (
    _build_sublattice_graph,
    _dispatch_sublattice,
    _gather_deps,
    _post_process,
    _run_abstract_task,
    _run_task,
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
    result_object = Result(received_workflow, "/tmp", "asdf")

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
async def test_dispatch_sublattice(test_db, mocker):
    @ct.electron(executor="local")
    def task(x):
        return x

    @ct.lattice(executor="local", workflow_executor="local")
    def sub_workflow(x):
        return task(x)

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._core.dispatcher.datasvc.unregister_dispatch")

    result_object = get_mock_result()

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
    sub_result_obj = get_result_object(sub_dispatch_id)
    assert sub_result_obj.dispatch_id == sub_dispatch_id
    assert sub_result_obj._electron_id == 1

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
