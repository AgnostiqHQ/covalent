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


import asyncio
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.pool import StaticPool

import covalent as ct
from covalent._results_manager import Result
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._workflow.lattice import Lattice
from covalent.executor.base import AsyncBaseExecutor
from covalent_dispatcher._core.runner_exp import (
    _get_task_result,
    _listen_for_job_events,
    _mark_failed,
    _mark_ready,
    _poll_task_status,
    _submit_abstract_task,
    run_abstract_task,
)
from covalent_dispatcher._dal.result import Result as SRVResult
from covalent_dispatcher._dal.result import get_result_object
from covalent_dispatcher._db import update
from covalent_dispatcher._db.datastore import DataStore

TEST_RESULTS_DIR = "/tmp/results"


class MockExecutor(AsyncBaseExecutor):
    async def run(self, function, args, kwargs, task_metadata):
        pass


class MockManagedExecutor(AsyncBaseExecutor):
    SUPPORTS_MANAGED_EXECUTION = True

    async def run(self, function, args, kwargs, task_metadata):
        pass

    def get_upload_uri(self, task_metadata, object_key):
        return f"file:///tmp/{object_key}"


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def get_mock_result() -> Result:
    """Construct a mock result object corresponding to a lattice."""

    import sys

    @ct.electron(executor="local")
    def task(x):
        print(f"stdout: {x}")
        print("Error!", file=sys.stderr)
        return x

    @ct.lattice(deps_bash=ct.DepsBash(["ls"]))
    def pipeline(x):
        res1 = task(x)
        res2 = task(res1)
        return res2

    pipeline.build_graph(x="absolute")
    received_workflow = Lattice.deserialize_from_json(pipeline.serialize_to_json())
    result_object = Result(received_workflow, "pipeline_workflow")

    return result_object


def get_mock_srvresult(sdkres, test_db) -> SRVResult:

    sdkres._initialize_nodes()

    update.persist(sdkres)

    return get_result_object(sdkres.dispatch_id)


@pytest.mark.asyncio
async def test_submit_abstract_task(mocker):

    import datetime

    me = MockManagedExecutor()
    me.send = AsyncMock(return_value="42")

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.get_electron_attribute",
        return_value="managed_dask",
    )

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.get_executor",
        return_value=me,
    )

    ts = datetime.datetime.now()

    node_result = {
        "node_id": 0,
        "start_time": ts,
        "status": "RUNNING",
    }

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.generate_node_result",
        return_value=node_result,
    )

    mock_upload = mocker.patch(
        "covalent_dispatcher._core.data_modules.asset_manager.upload_asset_for_nodes",
    )

    dispatch_id = "dispatch"
    task_id = 0
    name = "task"
    abstract_inputs = {"args": [1], "kwargs": {"key": 2}}
    task_metadata = {"dispatch_id": dispatch_id, "node_id": task_id}

    mock_function_uri = me.get_upload_uri(task_metadata, "function")
    mock_deps_uri = me.get_upload_uri(task_metadata, "deps")
    mock_cb_uri = me.get_upload_uri(task_metadata, "call_before")
    mock_ca_uri = me.get_upload_uri(task_metadata, "call_after")
    mock_node_upload_uri_1 = me.get_upload_uri(task_metadata, "node_1")
    mock_node_upload_uri_2 = me.get_upload_uri(task_metadata, "node_2")

    await _submit_abstract_task(dispatch_id, task_id, name, abstract_inputs, me)

    mock_upload.assert_awaited()

    me.send.assert_awaited_with(
        mock_function_uri,
        mock_deps_uri,
        mock_cb_uri,
        mock_ca_uri,
        [mock_node_upload_uri_1],
        {"key": mock_node_upload_uri_2},
        task_metadata,
    )


@pytest.mark.asyncio
async def test_submit_requires_opt_in(mocker):
    """Checks submit rejects old-style executors"""

    import datetime

    me = MockExecutor()
    me.send = AsyncMock(return_value="42")
    ts = datetime.datetime.now()
    dispatch_id = "dispatch"
    task_id = 0
    name = "task"
    abstract_inputs = {"args": [1], "kwargs": {"key": 2}}

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.get_electron_attribute",
        return_value="managed_dask",
    )

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.get_executor",
        return_value=me,
    )

    error_msg = str(NotImplementedError("Executor does not support managed execution"))

    node_result = {
        "node_id": 0,
        "end_time": ts,
        "status": RESULT_STATUS.FAILED,
        "error": error_msg,
    }

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.generate_node_result",
        return_value=node_result,
    )

    assert node_result == await _submit_abstract_task(
        dispatch_id, task_id, name, abstract_inputs, me
    )


@pytest.mark.asyncio
async def test_submit_rejects_sublattices(mocker):
    """Checks submit rejects sublattices (not yet supported)"""
    import datetime

    from covalent._shared_files.defaults import sublattice_prefix

    me = MockManagedExecutor()
    me.send = AsyncMock(return_value="42")
    ts = datetime.datetime.now()
    dispatch_id = "dispatch"
    task_id = 0
    name = sublattice_prefix
    abstract_inputs = {"args": [1], "kwargs": {"key": 2}}

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.get_electron_attribute",
        return_value="managed_dask",
    )

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.get_executor",
        return_value=me,
    )

    error_msg = str(NotImplementedError("Sublattices not yet supported"))

    node_result = {
        "node_id": 0,
        "end_time": ts,
        "status": RESULT_STATUS.FAILED,
        "error": error_msg,
    }

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.generate_node_result",
        return_value=node_result,
    )

    assert node_result == await _submit_abstract_task(
        dispatch_id, task_id, name, abstract_inputs, me
    )


@pytest.mark.asyncio
async def test_get_task_result(mocker):

    import datetime

    me = MockManagedExecutor()
    asset_uri = "file:///tmp/asset.pkl"
    me.receive = AsyncMock(return_value=(asset_uri, asset_uri, asset_uri, False))

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.get_electron_attribute",
        return_value="managed_dask",
    )

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.get_executor",
        return_value=me,
    )

    ts = datetime.datetime.now()

    node_result = {
        "node_id": 0,
        "start_time": ts,
        "end_time": ts,
        "status": RESULT_STATUS.COMPLETED,
    }

    expected_node_result = {
        "node_id": 0,
        "start_time": ts,
        "end_time": ts,
        "status": RESULT_STATUS.COMPLETED,
        "output_uri": asset_uri,
        "stdout_uri": asset_uri,
        "stderr_uri": asset_uri,
    }

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.generate_node_result",
        return_value=node_result,
    )

    mock_update = mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.update_node_result_refs",
    )

    mock_upload = mocker.patch(
        "covalent_dispatcher._core.data_modules.asset_manager.upload_asset_for_nodes",
    )

    dispatch_id = "dispatch"
    task_id = 0
    name = "task"

    task_metadata = {"dispatch_id": dispatch_id, "node_id": task_id}
    mock_job_handles = {(dispatch_id, task_id): 42}

    mocker.patch("covalent_dispatcher._core.runner_exp._job_handles", mock_job_handles)

    await _get_task_result(task_metadata)

    me.receive.assert_awaited_with(task_metadata, 42)

    mock_update.assert_awaited_with(dispatch_id, expected_node_result)

    # Test exception during get
    me.receive = AsyncMock(side_effect=RuntimeError())
    mock_update.reset_mock()

    await _get_task_result(task_metadata)
    mock_update.assert_awaited()


@pytest.mark.asyncio
async def test_poll_status(mocker):

    me = MockManagedExecutor()
    me.poll = AsyncMock(return_value=0)
    mocker.patch(
        "covalent_dispatcher._core.runner_exp.get_executor",
        return_value=me,
    )
    mock_mark_ready = mocker.patch(
        "covalent_dispatcher._core.runner_exp._mark_ready",
    )

    dispatch_id = "dispatch"
    task_id = 1
    task_metadata = {"dispatch_id": dispatch_id, "node_id": task_id}

    mock_job_handles = {(dispatch_id, task_id): 42}

    mocker.patch("covalent_dispatcher._core.runner_exp._job_handles", mock_job_handles)

    await _poll_task_status(task_metadata, me)

    mock_mark_ready.assert_awaited()

    me.poll = AsyncMock(return_value=-1)
    mock_mark_ready.reset_mock()

    await _poll_task_status(task_metadata, me)
    mock_mark_ready.assert_not_awaited()

    me.poll = AsyncMock(side_effect=RuntimeError())
    mock_mark_ready.reset_mock()
    mock_mark_failed = mocker.patch(
        "covalent_dispatcher._core.runner_exp._mark_failed",
    )

    await _poll_task_status(task_metadata, me)
    mock_mark_ready.assert_not_awaited()
    mock_mark_failed.assert_awaited()


@pytest.mark.asyncio
async def test_event_listener(mocker):
    import datetime

    ts = datetime.datetime.now()
    node_result = {
        "node_id": 0,
        "start_time": ts,
        "end_time": ts,
        "status": RESULT_STATUS.FAILED,
        "error": "error",
    }

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.generate_node_result",
        return_value=node_result,
    )

    mock_update = mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.update_node_result_refs",
    )

    mock_get = mocker.patch("covalent_dispatcher._core.runner_exp._get_task_result")

    task_metadata = {"dispatch_id": "dispatch", "node_id": 1}

    job_events = [{"event": "READY", "task_metadata": task_metadata}, {"event": "BYE"}]

    mock_event_queue = asyncio.Queue()

    mocker.patch(
        "covalent_dispatcher._core.runner_exp._job_events",
        mock_event_queue,
    )
    fut = asyncio.create_task(_listen_for_job_events())
    await _mark_ready(task_metadata)
    await _mark_ready(task_metadata)
    await mock_event_queue.put({"event": "BYE"})

    await asyncio.wait_for(fut, 1)

    assert mock_get.call_count == 2

    mock_get.reset_mock()

    fut = asyncio.create_task(_listen_for_job_events())

    await _mark_failed(task_metadata, "error")
    await mock_event_queue.put({"event": "BYE"})

    await asyncio.wait_for(fut, 1)

    mock_update.assert_awaited_with(task_metadata["dispatch_id"], node_result)

    await mock_event_queue.put({"BAD_EVENT": "asdf"})
    await mock_event_queue.put({"event": "BYE"})
    mock_log = mocker.patch("covalent_dispatcher._core.runner_exp.app_log.exception")

    fut = asyncio.create_task(_listen_for_job_events())

    await _mark_failed(task_metadata, "error")
    await mock_event_queue.put({"event": "BYE"})

    await asyncio.wait_for(fut, 1)


@pytest.mark.asyncio
async def test_run_abstract_task(mocker):
    mock_listen = AsyncMock()
    me = MockManagedExecutor()
    me.poll = AsyncMock(return_value=0)
    mocker.patch(
        "covalent_dispatcher._core.runner_exp.get_executor",
        return_value=me,
    )

    mock_poll = mocker.patch(
        "covalent_dispatcher._core.runner_exp._poll_task_status",
    )

    node_result = {"node_id": 0, "status": RESULT_STATUS.RUNNING}

    mock_submit = mocker.patch(
        "covalent_dispatcher._core.runner_exp._submit_abstract_task", return_value=node_result
    )

    mock_update = mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.update_node_result_refs",
    )

    dispatch_id = "dispatch"
    node_id = 0
    node_name = "task"
    abstract_inputs = {"args": [], "kwargs": {}}
    selected_executor = ["local", {}]
    workflow_executor = selected_executor
    await run_abstract_task(
        dispatch_id,
        node_id,
        node_name,
        abstract_inputs,
        selected_executor,
        workflow_executor,
    )

    mock_submit.assert_awaited()
    mock_update.assert_awaited()
    mock_poll.assert_awaited()


@pytest.mark.asyncio
async def test_run_abstract_task_handles_old_execs(mocker):
    mock_listen = AsyncMock()
    me = MockExecutor()
    mocker.patch(
        "covalent_dispatcher._core.runner_exp.get_executor",
        return_value=me,
    )

    mock_legacy_run = mocker.patch("covalent_dispatcher._core.runner.run_abstract_task")

    mock_submit = mocker.patch("covalent_dispatcher._core.runner_exp._submit_abstract_task")

    dispatch_id = "dispatch"
    node_id = 0
    node_name = "task"
    abstract_inputs = {"args": [], "kwargs": {}}
    selected_executor = ["local", {}]
    workflow_executor = selected_executor

    await run_abstract_task(
        dispatch_id,
        node_id,
        node_name,
        abstract_inputs,
        selected_executor,
        workflow_executor,
    )

    mock_legacy_run.assert_called()
    mock_submit.assert_not_awaited()


@pytest.mark.asyncio
async def test_run_abstract_task_handles_sublattices(mocker):
    """Check that sublattices are redirected to old runner"""

    from covalent._shared_files.defaults import sublattice_prefix

    me = MockExecutor()
    mocker.patch(
        "covalent_dispatcher._core.runner_exp.get_executor",
        return_value=me,
    )

    mock_legacy_run = mocker.patch("covalent_dispatcher._core.runner.run_abstract_task")

    mock_submit = mocker.patch("covalent_dispatcher._core.runner_exp._submit_abstract_task")

    dispatch_id = "dispatch"
    node_id = 0
    node_name = sublattice_prefix
    abstract_inputs = {"args": [], "kwargs": {}}
    selected_executor = ["local", {}]
    workflow_executor = selected_executor

    await run_abstract_task(
        dispatch_id,
        node_id,
        node_name,
        abstract_inputs,
        selected_executor,
        workflow_executor,
    )

    mock_legacy_run.assert_called()
    mock_submit.assert_not_awaited()


@pytest.mark.asyncio
async def test_run_abstract_task_handles_bad_executors(mocker):
    """Check handling of executors during get_executor"""

    from covalent._shared_files.defaults import sublattice_prefix

    mocker.patch("covalent_dispatcher._core.runner_exp.get_executor", side_effect=RuntimeError())

    mock_update = mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.update_node_result_refs",
    )
    dispatch_id = "dispatch"
    node_id = 0
    node_name = sublattice_prefix
    abstract_inputs = {"args": [], "kwargs": {}}
    selected_executor = ["local", {}]
    workflow_executor = selected_executor

    await run_abstract_task(
        dispatch_id,
        node_id,
        node_name,
        abstract_inputs,
        selected_executor,
        workflow_executor,
    )

    mock_update.assert_awaited()
