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

"""Unit tests for the Result object."""

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

import covalent as ct
from covalent._results_manager.result import Result
from covalent._workflow.lattice import Lattice as LatticeClass
from covalent.executor import LocalExecutor
from covalent.executor._runtime.utils import ExecutorCache

TEMP_RESULTS_DIR = "/tmp/results"


def get_mock_result() -> Result:
    """Construct a mock result object corresponding to a lattice."""

    import sys

    @ct.electron(executor="local")
    def task(x):
        print(f"stdout: {x}")
        print("Error!", file=sys.stderr)
        return x

    @ct.lattice(results_dir=TEMP_RESULTS_DIR)
    def pipeline(x):
        res1 = task(x)
        res2 = task(res1)
        return res2

    pipeline.build_graph(x="absolute")
    received_workflow = LatticeClass.deserialize_from_json(pipeline.serialize_to_json())
    result_object = Result(
        received_workflow, pipeline.metadata["results_dir"], "pipeline_workflow"
    )

    return result_object


def get_mock_sublattice_result() -> Result:
    """Construct a mock result object whose transport graph contains a
    sublattice."""

    import sys

    @ct.electron(executor="local")
    def task(x):
        print(f"stdout: {x}")
        print("Error!", file=sys.stderr)
        return x

    @ct.electron
    @ct.lattice
    def sub_workflow(x):
        return task(x)

    @ct.lattice(results_dir=TEMP_RESULTS_DIR)
    def workflow(x):
        res1 = task(x)
        res2 = sub_workflow(res1)
        return res2

    workflow.build_graph(x=1)
    received_workflow = LatticeClass.deserialize_from_json(workflow.serialize_to_json())
    result_object = Result(received_workflow, workflow.metadata["results_dir"], "root_workflow")

    return result_object


le = LocalExecutor(log_stdout="/tmp/stdout.log")


@pytest.fixture
def result_1():
    @ct.electron(executor="dask")
    def task_1(x, y):
        return x * y

    @ct.electron(executor=le)
    def task_2(x, y):
        return x + y

    @ct.lattice(executor=le, workflow_executor=le, results_dir=TEMP_RESULTS_DIR)
    def workflow_1(a, b):
        """Docstring"""
        res_1 = task_1(a, b)
        return task_2(res_1, b)

    Path(f"{TEMP_RESULTS_DIR}/dispatch_1").mkdir(parents=True, exist_ok=True)
    workflow_1.build_graph(a=1, b=2)
    received_lattice = LatticeClass.deserialize_from_json(workflow_1.serialize_to_json())
    result = Result(
        lattice=received_lattice, results_dir=TEMP_RESULTS_DIR, dispatch_id="dispatch_1"
    )
    result.lattice.metadata["results_dir"] = TEMP_RESULTS_DIR
    result._initialize_nodes()
    return result


def test_get_node_error(result_1):
    """Test result method to get the node error."""
    assert not result_1._get_node_error(node_id=0)


def test_get_all_node_results(result_1, mocker):
    """Test result method to get all the node results."""

    for data_row in result_1.get_all_node_results():
        if data_row["node_id"] == 0:
            assert data_row["node_name"] == "task_1"
        elif data_row["node_id"] == 1:
            assert data_row["node_name"] == ":parameter:1"


def test_result_root_dispatch_id(result_1):
    """Test the `root_dispatch_id` property`"""

    assert result_1.root_dispatch_id == result_1._root_dispatch_id


def test_result_post_process(
    mocker,
):
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

    compute_energy = LatticeClass.deserialize_from_json(compute_energy.serialize_to_json())

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
    res._root_dispatch_id = "MOCK"

    execution_result = res.post_process()

    assert execution_result == compute_energy()


def test_getstate(mocker):
    """Test result.__getstate__()"""

    result_object = get_mock_result()
    result_object._initialize_runtime_state()
    state = result_object.__getstate__()
    assert state["_runtime_state"] == {}


def test_get_executor_cache(mocker):
    result_object = get_mock_result()
    result_object._initialize_runtime_state()
    cache_init = mocker.patch(
        "covalent.executor._runtime.utils.ExecutorCache.__init__", return_value=None
    )
    cache = result_object._get_executor_cache()
    cache_init.assert_called_once_with(result_object)


def test_set_executor_cache(mocker):
    result_object = get_mock_result()
    cache = ExecutorCache()
    result_object._initialize_runtime_state()
    result_object._set_executor_cache(cache)
    assert result_object._runtime_state["executor_cache"] == cache


def test_get_tasks_queue():
    """Test _get_tasks_queue"""
    result_object = get_mock_result()
    result_object._initialize_runtime_state()
    q = result_object._get_tasks_queue()
    assert q == result_object._get_tasks_queue()


def test_get_workflow_exec_task_id():
    """Test _get_workflow_executor_task_id"""
    result_object = get_mock_result()
    result_object._initialize_runtime_state()
    assert result_object._get_workflow_executor_task_id() == -1
    assert result_object._get_workflow_executor_task_id() == -2


def test_cancel_called_property():
    """Test the _cancel_called property"""
    result_object = get_mock_result()
    result_object._initialize_runtime_state()
    result_object._cancel_called = True

    assert result_object._cancel_called is True


@pytest.mark.asyncio
async def test_cancel_workflow(mocker):
    """Test Result._cancel()"""

    result_object = get_mock_sublattice_result()
    result_object._initialize_nodes()
    result_object._initialize_runtime_state()
    cache = ExecutorCache()
    result_object._set_executor_cache(cache)
    mock_finalize = mocker.patch(
        "covalent.executor._runtime.utils.ExecutorCache.finalize_executors"
    )
    mock_put = mocker.patch("asyncio.Queue.put")
    subresult_object = get_mock_result()
    subresult_object._cancel = AsyncMock()
    tg = result_object.lattice.transport_graph
    tg.set_node_value(2, "sublattice_result", subresult_object)

    await result_object._cancel()

    mock_put.assert_awaited_once_with(-1)
    assert result_object._cancel_called is True
    mock_finalize.assert_awaited()

    subresult_object._cancel.assert_awaited_once()


@pytest.mark.asyncio
async def test_cancel_completed_workflow(mocker):
    """Test Result._cancel() for completed or already cancelled workflows"""

    result_object = get_mock_sublattice_result()
    result_object._initialize_nodes()
    result_object._initialize_runtime_state()
    result_object._status = Result.COMPLETED
    cache = ExecutorCache()
    result_object._set_executor_cache(cache)
    mock_finalize = mocker.patch(
        "covalent.executor._runtime.utils.ExecutorCache.finalize_executors"
    )
    mock_put = mocker.patch("asyncio.Queue.put")
    subresult_object = get_mock_result()
    subresult_object._cancel = AsyncMock()
    tg = result_object.lattice.transport_graph
    tg.set_node_value(2, "sublattice_result", subresult_object)

    await result_object._cancel()

    mock_put.assert_not_awaited()
    assert not result_object._cancel_called
    mock_finalize.assert_not_awaited()

    subresult_object._cancel.assert_not_awaited()
