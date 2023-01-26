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


import pytest

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.dispatcher import (
    _finalize_dispatch,
    _handle_cancelled_node,
    _handle_event,
    _handle_failed_node,
    _handle_node_status_update,
    _submit_initial_tasks,
    _submit_task,
    cancel_workflow,
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


@pytest.mark.asyncio
async def test_handle_failed_node(mocker):
    """Unit test for failed node handler"""
    dispatch_id = "failed_dispatch"
    await _handle_failed_node(dispatch_id, 1)


@pytest.mark.asyncio
async def test_handle_cancelled_node(mocker, test_db):
    """Unit test for cancelled node handler"""
    dispatch_id = "cancelled_dispatch"

    await _handle_cancelled_node(dispatch_id, 1)


@pytest.mark.parametrize(
    "wait,expected_status", [(True, Result.COMPLETED), (False, Result.RUNNING)]
)
@pytest.mark.asyncio
async def test_run_workflow_normal(mocker, wait, expected_status):
    import asyncio

    dispatch_id = "mock_dispatch"

    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )
    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_dispatch_attributes",
        return_value={"status": Result.NEW_OBJ},
    )
    _futures = {dispatch_id: asyncio.Future()}
    mocker.patch("covalent_dispatcher._core.dispatcher._futures", _futures)

    async def mark_future_done(dispatch_id):
        _futures[dispatch_id].set_result(Result.COMPLETED)
        return Result.RUNNING

    mocker.patch(
        "covalent_dispatcher._core.dispatcher._submit_initial_tasks",
        return_value=Result.RUNNING,
        side_effect=mark_future_done,
    )

    dispatch_status = await run_workflow(dispatch_id, wait)
    assert dispatch_status == expected_status
    if wait:
        mock_unregister.assert_called_with(dispatch_id)


@pytest.mark.asyncio
async def test_run_completed_workflow(mocker):
    import asyncio

    dispatch_id = "completed_dispatch"
    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_dispatch_attributes",
        return_value={"status": Result.COMPLETED},
    )

    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )
    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_dispatch_attributes",
        return_value={"status": Result.COMPLETED},
    )
    mock_plan = mocker.patch("covalent_dispatcher._core.dispatcher._plan_workflow")
    dispatch_status = await run_workflow(dispatch_id)

    mock_unregister.assert_called_with(dispatch_id)
    assert dispatch_status == Result.COMPLETED


@pytest.mark.asyncio
async def test_run_workflow_exception(mocker):
    import asyncio

    dispatch_id = "mock_dispatch"

    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )
    mocker.patch("covalent_dispatcher._core.dispatcher._plan_workflow")
    mocker.patch(
        "covalent_dispatcher._core.dispatcher._submit_initial_tasks",
        side_effect=RuntimeError("Error"),
    )

    mock_update_dispatch_result = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.update_dispatch_result",
    )
    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_dispatch_attributes",
        return_value={"status": Result.NEW_OBJ},
    )

    status = await run_workflow(dispatch_id)

    assert status == Result.FAILED
    mock_unregister.assert_called_with(dispatch_id)


@pytest.mark.asyncio
async def test_run_dispatch(mocker):

    dispatch_id = "test_dispatch"
    mock_run = mocker.patch("covalent_dispatcher._core.dispatcher.run_workflow")
    run_dispatch(dispatch_id)
    mock_run.assert_called_with(dispatch_id)


@pytest.mark.asyncio
async def test_handle_completed_node_update(mocker):
    import asyncio

    dispatch_id = "mock_dispatch"
    node_id = 2
    status = Result.COMPLETED
    detail = {}
    ready_nodes = [0, 1]

    mock_handle_cancelled = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_completed_node", return_value=ready_nodes
    )
    mock_decrement = mocker.patch(
        "covalent_dispatcher._core.dispatcher._unresolved_tasks.decrement"
    )

    mock_increment = mocker.patch(
        "covalent_dispatcher._core.dispatcher._unresolved_tasks.increment"
    )
    mock_submit_task = mocker.patch("covalent_dispatcher._core.dispatcher._submit_task")

    await _handle_node_status_update(dispatch_id, node_id, status, detail)
    mock_decrement.assert_awaited()
    assert mock_increment.await_count == 2
    assert mock_submit_task.await_count == 2


@pytest.mark.asyncio
async def test_handle_cancelled_node_update(mocker):
    import asyncio

    dispatch_id = "mock_dispatch"
    node_id = 0
    status = Result.CANCELLED
    detail = {}
    mock_handle_cancelled = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_cancelled_node",
    )
    mock_decrement = mocker.patch(
        "covalent_dispatcher._core.dispatcher._unresolved_tasks.decrement"
    )

    await _handle_node_status_update(dispatch_id, node_id, status, detail)
    mock_handle_cancelled.assert_awaited_with(dispatch_id, 0)
    mock_decrement.assert_awaited()


@pytest.mark.asyncio
async def test_run_handle_failed_node_update(mocker):
    import asyncio

    dispatch_id = "mock_dispatch"
    node_id = 0
    status = Result.FAILED
    detail = {}
    mock_handle_failed = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_failed_node",
    )
    mock_decrement = mocker.patch(
        "covalent_dispatcher._core.dispatcher._unresolved_tasks.decrement"
    )

    await _handle_node_status_update(dispatch_id, node_id, status, detail)
    mock_handle_failed.assert_awaited_with(dispatch_id, 0)
    mock_decrement.assert_awaited()


@pytest.mark.asyncio
async def test_run_handle_sublattice_node_update(mocker):
    import asyncio

    from covalent._shared_files.util_classes import RESULT_STATUS

    dispatch_id = "mock_dispatch"
    node_id = 0
    status = RESULT_STATUS.DISPATCHING
    detail = {"sub_dispatch_id": "sub_dispatch"}
    mock_run_dispatch = mocker.patch(
        "covalent_dispatcher._core.dispatcher.run_dispatch",
    )
    mock_decrement = mocker.patch(
        "covalent_dispatcher._core.dispatcher._unresolved_tasks.decrement"
    )
    await _handle_node_status_update(dispatch_id, node_id, status, detail)
    mock_run_dispatch.assert_called_with("sub_dispatch")
    mock_decrement.assert_not_awaited()


@pytest.mark.parametrize("unresolved_count", [1, 0])
@pytest.mark.asyncio
async def test_handle_event(mocker, unresolved_count):
    mock_handle_status_update = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_node_status_update",
    )
    mock_handle_dispatch_exception = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_dispatch_exception",
    )

    mock_persist = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.persist_result",
    )

    mock_finalize = mocker.patch(
        "covalent_dispatcher._core.dispatcher._finalize_dispatch",
        return_value=Result.COMPLETED,
    )

    mock_get_unresolved = mocker.patch(
        "covalent_dispatcher._core.dispatcher._unresolved_tasks.get_unresolved",
        return_value=unresolved_count,
    )

    dispatch_id = "mock_dispatch"
    node_id = 2
    status = Result.COMPLETED
    msg = {"dispatch_id": dispatch_id, "node_id": node_id, "status": status, "detail": {}}

    await _handle_event(msg)

    if unresolved_count < 1:
        mock_finalize.assert_awaited()
        mock_persist.assert_awaited()
    else:
        mock_finalize.assert_not_awaited


@pytest.mark.asyncio
async def test_handle_event_exception(mocker):
    import asyncio

    mock_handle_status_update = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_node_status_update",
        side_effect=RuntimeError(),
    )
    mock_handle_dispatch_exception = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_dispatch_exception",
        return_value=Result.FAILED,
    )

    mock_persist = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.persist_result",
    )

    mock_finalize = mocker.patch(
        "covalent_dispatcher._core.dispatcher._finalize_dispatch",
        return_value=Result.COMPLETED,
    )

    mock_get_unresolved = mocker.patch(
        "covalent_dispatcher._core.dispatcher._unresolved_tasks.get_unresolved",
        return_value=2,
    )

    dispatch_id = "mock_dispatch"
    node_id = 2
    status = Result.COMPLETED
    msg = {"dispatch_id": dispatch_id, "node_id": node_id, "status": status, "detail": {}}

    _futures = {dispatch_id: asyncio.Future()}

    mocker.patch(
        "covalent_dispatcher._core.dispatcher._futures",
        _futures,
    )

    assert await _handle_event(msg) == Result.FAILED

    assert _futures[dispatch_id].result() == Result.FAILED

    mock_persist.assert_awaited()
    mock_finalize.assert_not_awaited


@pytest.mark.asyncio
async def test_handle_event_finalize_exception(mocker):
    import asyncio

    mock_handle_status_update = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_node_status_update",
    )
    mock_handle_dispatch_exception = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_dispatch_exception",
        return_value=Result.FAILED,
    )

    mock_persist = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.persist_result",
    )

    mock_finalize = mocker.patch(
        "covalent_dispatcher._core.dispatcher._finalize_dispatch",
        side_effect=RuntimeError(),
    )

    mock_get_unresolved = mocker.patch(
        "covalent_dispatcher._core.dispatcher._unresolved_tasks.get_unresolved",
        return_value=0,
    )

    dispatch_id = "mock_dispatch"
    node_id = 2
    status = Result.COMPLETED
    msg = {"dispatch_id": dispatch_id, "node_id": node_id, "status": status, "detail": {}}

    _futures = {dispatch_id: asyncio.Future()}

    mocker.patch(
        "covalent_dispatcher._core.dispatcher._futures",
        _futures,
    )

    assert await _handle_event(msg) == Result.FAILED

    assert _futures[dispatch_id].result() == Result.FAILED

    mock_persist.assert_awaited()


@pytest.mark.parametrize(
    "failed,cancelled,final_status",
    [
        (False, False, Result.COMPLETED),
        (False, True, Result.CANCELLED),
        (True, False, Result.FAILED),
        (True, True, Result.FAILED),
    ],
)
@pytest.mark.asyncio
async def test_finalize_dispatch(mocker, failed, cancelled, final_status):
    mock_remove = mocker.patch("covalent_dispatcher._core.dispatcher._unresolved_tasks.remove")

    failed_tasks = [(0, "task_0")] if failed else []
    cancelled_tasks = [(1, "task_1")] if cancelled else []

    query_result = {"failed": failed_tasks, "cancelled": cancelled_tasks}
    mock_incomplete = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_incomplete_tasks",
        return_value=query_result,
    )

    mock_dispatch_info = {"status": Result.COMPLETED}

    def mock_gen_dispatch_result(dispatch_id, **kwargs):
        return {"status": kwargs["status"]}

    async def mock_update_dispatch_result(dispatch_id, dispatch_result):
        mock_dispatch_info["status"] = dispatch_result["status"]

    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.generate_dispatch_result",
        mock_gen_dispatch_result,
    )

    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.update_dispatch_result",
        mock_update_dispatch_result,
    )

    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_dispatch_attributes",
        return_value=mock_dispatch_info,
    )

    dispatch_id = "dispatch_1"

    assert await _finalize_dispatch(dispatch_id) == final_status


@pytest.mark.asyncio
async def test_submit_initial_tasks(mocker):
    dispatch_id = "dispatch_1"

    initial_nodes = [1, 2]
    mocker.patch(
        "covalent_dispatcher._core.dispatcher._get_initial_tasks_and_deps",
        return_value=(3, initial_nodes, {}),
    )
    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.generate_dispatch_result",
    )
    mocker.patch(
        "covalent_dispatcher._core.dispatcher._initialize_caches",
    )

    mock_inc = mocker.patch("covalent_dispatcher._core.dispatcher._unresolved_tasks.increment")
    mock_submit_task = mocker.patch(
        "covalent_dispatcher._core.dispatcher._submit_task",
    )
    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.update_dispatch_result",
    )

    assert await _submit_initial_tasks(dispatch_id) == Result.RUNNING

    assert mock_submit_task.await_count == 2
    assert mock_inc.await_count == 2


@pytest.mark.parametrize("new_runner", [True, False])
@pytest.mark.asyncio
async def test_submit_task(mocker, new_runner):
    dispatch_id = "dispatch_1"
    node_id = 2

    mocker.patch(
        "covalent_dispatcher._core.dispatcher._get_abstract_task_inputs",
        return_value={"args": [], "kwargs": {}},
    )

    mocker.patch(
        "covalent_dispatcher._core.dispatcher.NEW_RUNNER_ENABLED",
        new_runner,
    )

    mock_attrs = {
        "name": "task",
        "value": 5,
        "executor": "local",
        "executor_data": {},
    }

    async def get_electron_attr(dispatch_id, node_id, key):
        return mock_attrs[key]

    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_electron_attribute",
        get_electron_attr,
    )

    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.update_node_result",
    )

    mock_run_abs_task = mocker.patch(
        "covalent_dispatcher._core.dispatcher.runner_exp.run_abstract_task",
    )
    mock_run_abs_task_legacy = mocker.patch(
        "covalent_dispatcher._core.dispatcher.runner.run_abstract_task",
    )

    await _submit_task(dispatch_id, node_id)

    if new_runner:
        mock_run_abs_task.assert_called()
    else:
        mock_run_abs_task_legacy.assert_called()


@pytest.mark.asyncio
async def test_submit_parameter(mocker):
    from covalent._shared_files.defaults import parameter_prefix

    dispatch_id = "dispatch_1"
    node_id = 2

    mock_attrs = {
        "name": parameter_prefix,
        "value": 5,
        "executor": "local",
        "executor_data": {},
    }

    async def get_electron_attr(dispatch_id, node_id, key):
        return mock_attrs[key]

    mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.get_electron_attribute",
        get_electron_attr,
    )

    mock_update = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.update_node_result",
    )

    mock_run_abs_task = mocker.patch(
        "covalent_dispatcher._core.dispatcher.runner_exp.run_abstract_task",
    )
    mock_run_abs_task_legacy = mocker.patch(
        "covalent_dispatcher._core.dispatcher.runner.run_abstract_task",
    )

    await _submit_task(dispatch_id, node_id)

    mock_run_abs_task.assert_not_called()
    mock_run_abs_task_legacy.assert_not_called()
    mock_update.assert_awaited()


def test_cancelled_workflow():
    cancel_workflow("asdf")
