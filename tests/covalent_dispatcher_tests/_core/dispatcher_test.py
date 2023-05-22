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


from typing import Dict, List
from unittest.mock import AsyncMock, call

import cloudpickle as pickle
import pytest
from mock import MagicMock

import covalent as ct
from covalent._results_manager import Result
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.dispatcher import (
    _get_abstract_task_inputs,
    _get_initial_tasks_and_deps,
    _handle_cancelled_node,
    _handle_completed_node,
    _handle_failed_node,
    _plan_workflow,
    _run_planned_workflow,
    _submit_task,
    cancel_dispatch,
    run_dispatch,
    run_workflow,
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

    @ct.lattice
    def pipeline(x):
        res1 = task(x)
        res2 = task(res1)
        return res2

    pipeline.build_graph(x="absolute")
    received_workflow = Lattice.deserialize_from_json(pipeline.serialize_to_json())
    result_object = Result(received_workflow, "pipeline_workflow")

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
    result_object = Result(received_workflow, "asdf")
    _plan_workflow(result_object=result_object)

    # Updated transport graph post planning
    updated_tg = pickle.loads(result_object.lattice.transport_graph.serialize(metadata_only=True))

    assert updated_tg["lattice_metadata"]["schedule"]


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

    result_object = Result(lattice=list_workflow, dispatch_id="asdf")
    abs_task_inputs = _get_abstract_task_inputs(1, tg.get_node_value(1, "name"), result_object)

    expected_inputs = {"args": abstract_args, "kwargs": {}}

    assert abs_task_inputs == expected_inputs

    # dict-type inputs

    # Nodes 0=task, 1=:electron_dict:, 2=1, 3=2
    dict_workflow.build_graph({"a": 1, "b": 2})
    abstract_args = {"a": 2, "b": 3}
    tg = dict_workflow.transport_graph

    result_object = Result(lattice=dict_workflow, dispatch_id="asdf")
    task_inputs = _get_abstract_task_inputs(1, tg.get_node_value(1, "name"), result_object)
    expected_inputs = {"args": [], "kwargs": abstract_args}

    assert task_inputs == expected_inputs

    # Check arg order
    multivar_workflow.build_graph(1, 2)
    received_lattice = Lattice.deserialize_from_json(multivar_workflow.serialize_to_json())
    result_object = Result(lattice=received_lattice, dispatch_id="asdf")
    tg = received_lattice.transport_graph

    assert list(tg._graph.nodes) == list(range(9))
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
    pending_parents = {}

    result_object = get_mock_result()

    # tg edges are (1, 0), (0, 2)
    pending_parents[0] = 1
    pending_parents[1] = 0
    pending_parents[2] = 1

    mock_upsert_lattice = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.upsert_lattice_data"
    )

    node_result = {"node_id": 1, "status": Result.COMPLETED}

    next_nodes = await _handle_completed_node(result_object, 1, pending_parents)
    assert next_nodes == [0]
    assert pending_parents == {0: 0, 1: 0, 2: 1}


@pytest.mark.asyncio
async def test_handle_failed_node(mocker):
    """Unit test for failed node handler"""
    pending_parents = {}

    result_object = get_mock_result()
    # tg edges are (1, 0), (0, 2)

    mock_upsert_lattice = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.upsert_lattice_data"
    )
    await _handle_failed_node(result_object, 1)

    mock_upsert_lattice.assert_called()


@pytest.mark.asyncio
async def test_handle_cancelled_node(mocker):
    """Unit test for cancelled node handler"""
    pending_parents = {}

    result_object = get_mock_result()
    # tg edges are (1, 0), (0, 2)

    mock_upsert_lattice = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.upsert_lattice_data"
    )

    node_result = {"node_id": 1, "status": Result.CANCELLED}

    await _handle_cancelled_node(result_object, 1)
    assert result_object._task_cancelled is True
    mock_upsert_lattice.assert_called()


@pytest.mark.asyncio
async def test_get_initial_tasks_and_deps(mocker):
    """Test internal function for initializing status_queue and pending_parents"""
    pending_parents = {}

    result_object = get_mock_result()
    num_tasks, initial_nodes, pending_parents = await _get_initial_tasks_and_deps(result_object)

    assert initial_nodes == [1]
    assert pending_parents == {0: 1, 1: 0, 2: 1, 3: 2}
    assert num_tasks == len(result_object.lattice.transport_graph._graph.nodes)


@pytest.mark.asyncio
async def test_run_dispatch(mocker):
    """
    Test running a mock dispatch
    """
    res = get_mock_result()
    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_result_object", return_value=res
    )
    mock_run = mocker.patch("covalent_dispatcher._core.dispatcher.run_workflow")
    run_dispatch(res.dispatch_id)
    mock_run.assert_called_with(res)


@pytest.mark.asyncio
async def test_run_workflow_normal(mocker):
    """
    Test a normal workflow execution
    """
    import asyncio

    result_object = get_mock_result()
    msg_queue = asyncio.Queue()
    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_status_queue", return_value=msg_queue
    )
    mocker.patch("covalent_dispatcher._core.dispatcher._plan_workflow")
    mocker.patch(
        "covalent_dispatcher._core.dispatcher._run_planned_workflow", return_value=result_object
    )
    mock_persist = mocker.patch("covalent_dispatcher._core.dispatcher.datasvc.persist_result")
    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )
    await run_workflow(result_object)

    mock_persist.assert_awaited_with(result_object.dispatch_id)
    mock_unregister.assert_called_with(result_object.dispatch_id)


@pytest.mark.asyncio
async def test_run_completed_workflow(mocker):
    """
    Test run completed workflow
    """
    import asyncio

    result_object = get_mock_result()
    result_object._status = Result.COMPLETED
    msg_queue = asyncio.Queue()
    mock_get_status_queue = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_status_queue", return_value=msg_queue
    )
    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )
    mock_plan = mocker.patch("covalent_dispatcher._core.dispatcher._plan_workflow")
    mocker.patch(
        "covalent_dispatcher._core.dispatcher._run_planned_workflow", return_value=result_object
    )
    mocker.patch("covalent_dispatcher._core.dispatcher.datasvc.persist_result")

    await run_workflow(result_object)

    mock_plan.assert_not_called()
    mock_get_status_queue.assert_not_called()
    mock_unregister.assert_called_with(result_object.dispatch_id)


@pytest.mark.asyncio
async def test_run_workflow_exception(mocker):
    """
    Test any exception raised when running workflow
    """
    import asyncio

    result_object = get_mock_result()
    msg_queue = asyncio.Queue()

    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_status_queue", return_value=msg_queue
    )
    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )
    mocker.patch("covalent_dispatcher._core.dispatcher._plan_workflow")
    mocker.patch(
        "covalent_dispatcher._core.dispatcher._run_planned_workflow",
        return_value=result_object,
        side_effect=RuntimeError("Error"),
    )
    mock_persist = mocker.patch("covalent_dispatcher._core.dispatcher.datasvc.persist_result")

    result = await run_workflow(result_object)

    assert result.status == Result.FAILED
    mock_persist.assert_awaited_with(result_object.dispatch_id)
    mock_unregister.assert_called_with(result_object.dispatch_id)


@pytest.mark.asyncio
async def test_run_planned_workflow_cancelled_update(mocker):
    """
    Test run planned workflow with cancelled update
    """
    import asyncio

    result_object = get_mock_result()

    mocker.patch("covalent_dispatcher._core.dispatcher.datasvc.upsert_lattice_data")
    tasks_left = 1
    initial_nodes = [0]
    pending_deps = {0: 0}

    mocker.patch(
        "covalent_dispatcher._core.dispatcher._get_initial_tasks_and_deps",
        return_value=(tasks_left, initial_nodes, pending_deps),
    )

    mock_submit_task = mocker.patch("covalent_dispatcher._core.dispatcher._submit_task")

    def side_effect(result_object, node_id):
        result_object._task_cancelled = True

    mock_handle_cancelled = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_cancelled_node", side_effect=side_effect
    )
    status_queue = asyncio.Queue()
    status_queue.put_nowait((0, Result.CANCELLED, {}))
    await _run_planned_workflow(result_object, status_queue)
    assert mock_submit_task.await_count == 1
    mock_handle_cancelled.assert_awaited_with(result_object, 0)


@pytest.mark.asyncio
async def test_run_planned_workflow_failed_update(mocker):
    """
    Test run planned workflow with mocking a failed job update
    """
    import asyncio

    result_object = get_mock_result()

    mocker.patch("covalent_dispatcher._core.dispatcher.datasvc.upsert_lattice_data")
    tasks_left = 1
    initial_nodes = [0]
    pending_deps = {0: 0}

    mocker.patch(
        "covalent_dispatcher._core.dispatcher._get_initial_tasks_and_deps",
        return_value=(tasks_left, initial_nodes, pending_deps),
    )

    mock_submit_task = mocker.patch("covalent_dispatcher._core.dispatcher._submit_task")

    def side_effect(result_object, node_id):
        result_object._task_failed = True

    mock_handle_failed = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_failed_node", side_effect=side_effect
    )
    status_queue = asyncio.Queue()
    status_queue.put_nowait((0, Result.FAILED, {}))
    await _run_planned_workflow(result_object, status_queue)
    assert mock_submit_task.await_count == 1
    mock_handle_failed.assert_awaited_with(result_object, 0)


@pytest.mark.asyncio
async def test_run_planned_workflow_dispatching(mocker):
    """Test the run planned workflow for a dispatching node."""
    import asyncio

    result_object = get_mock_result()

    mocker.patch("covalent_dispatcher._core.dispatcher.datasvc.upsert_lattice_data")
    tasks_left = 1
    initial_nodes = [0]
    pending_deps = {0: 0}

    mocker.patch(
        "covalent_dispatcher._core.dispatcher._get_initial_tasks_and_deps",
        return_value=(tasks_left, initial_nodes, pending_deps),
    )

    mock_submit_task = mocker.patch("covalent_dispatcher._core.dispatcher._submit_task")

    def side_effect(result_object, node_id):
        result_object._task_failed = True

    mock_handle_failed = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_failed_node", side_effect=side_effect
    )
    mock_run_dispatch = mocker.patch("covalent_dispatcher._core.dispatcher.run_dispatch")
    status_queue = asyncio.Queue()
    status_queue.put_nowait(
        (0, RESULT_STATUS.DISPATCHING_SUBLATTICE, {"sub_dispatch_id": "mock_sub_dispatch_id"})
    )
    status_queue.put_nowait((0, RESULT_STATUS.FAILED, {}))  # This ensures that the loop is exited.
    await _run_planned_workflow(result_object, status_queue)
    assert mock_submit_task.await_count == 1
    mock_handle_failed.assert_awaited_with(result_object, 0)
    mock_run_dispatch.assert_called_once_with("mock_sub_dispatch_id")


@pytest.mark.asyncio
async def test_cancel_dispatch(mocker):
    """Test cancelling a dispatch, including sub-lattices"""
    res = get_mock_result()
    sub_res = get_mock_result()

    sub_dispatch_id = "sub_pipeline_workflow"
    sub_res._dispatch_id = sub_dispatch_id

    def mock_get_result_object(dispatch_id):
        objs = {res._dispatch_id: res, sub_res._dispatch_id: sub_res}
        return objs[dispatch_id]

    mock_data_cancel = mocker.patch("covalent_dispatcher._core.dispatcher.set_cancel_requested")

    mock_runner = mocker.patch("covalent_dispatcher._core.dispatcher.runner")
    mock_runner.cancel_tasks = AsyncMock()

    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_result_object", mock_get_result_object
    )

    res._initialize_nodes()
    sub_res._initialize_nodes()

    tg = res.lattice.transport_graph
    tg.set_node_value(2, "sub_dispatch_id", sub_dispatch_id)
    sub_tg = sub_res.lattice.transport_graph

    await cancel_dispatch("pipeline_workflow")

    task_ids = list(tg._graph.nodes)
    sub_task_ids = list(sub_tg._graph.nodes)

    calls = [call("pipeline_workflow", task_ids), call(sub_dispatch_id, sub_task_ids)]
    mock_data_cancel.assert_has_awaits(calls)
    mock_runner.cancel_tasks.assert_has_awaits(calls)


@pytest.mark.asyncio
async def test_cancel_dispatch_with_task_ids(mocker):
    """Test cancelling a dispatch, including sub-lattices and with task ids"""
    res = get_mock_result()
    sub_res = get_mock_result()

    sub_dispatch_id = "sub_pipeline_workflow"
    sub_res._dispatch_id = sub_dispatch_id

    def mock_get_result_object(dispatch_id):
        objs = {res._dispatch_id: res, sub_res._dispatch_id: sub_res}
        return objs[dispatch_id]

    mock_data_cancel = mocker.patch("covalent_dispatcher._core.dispatcher.set_cancel_requested")

    mock_runner = mocker.patch("covalent_dispatcher._core.dispatcher.runner")
    mock_runner.cancel_tasks = AsyncMock()

    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_result_object", mock_get_result_object
    )
    mock_app_log = mocker.patch("covalent_dispatcher._core.dispatcher.app_log.debug")

    res._initialize_nodes()
    sub_res._initialize_nodes()

    tg = res.lattice.transport_graph
    tg.set_node_value(2, "sub_dispatch_id", sub_dispatch_id)
    sub_tg = sub_res.lattice.transport_graph
    task_ids = list(tg._graph.nodes)
    sub_task_ids = list(sub_tg._graph.nodes)

    await cancel_dispatch("pipeline_workflow", task_ids)

    calls = [call("pipeline_workflow", task_ids), call(sub_dispatch_id, sub_task_ids)]
    mock_data_cancel.assert_has_awaits(calls)
    mock_runner.cancel_tasks.assert_has_awaits(calls)
    assert mock_app_log.call_count == 2


@pytest.mark.asyncio
async def test_submit_task(mocker):
    """Test the submit task function."""

    def transport_graph_get_value_side_effect(node_id, key):
        if key == "name":
            return "mock-name"
        if key == "status":
            return RESULT_STATUS.COMPLETED

    mock_result = MagicMock()
    mock_result.lattice.transport_graph.get_node_value.side_effect = (
        transport_graph_get_value_side_effect
    )

    generate_node_result_mock = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.generate_node_result"
    )
    update_node_result_mock = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.update_node_result"
    )
    await _submit_task(mock_result, 0)
    assert mock_result.lattice.transport_graph.get_node_value.mock_calls == [
        call(0, "name"),
        call(0, "status"),
        call(0, "output"),
    ]
    update_node_result_mock.assert_called_with(mock_result, generate_node_result_mock.return_value)
    generate_node_result_mock.assert_called_once()
