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
    _submit_abstract_task_group,
    run_abstract_task_group,
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
async def test_submit_abstract_task_group(mocker):

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
    name = "task"
    abstract_inputs = {"args": [1], "kwargs": {"key": 2}}
    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "task_ids": [0, 3],
        "task_group_id": 0,
    }

    mock_function_uri_0 = me.get_upload_uri(task_group_metadata, "function-0")
    mock_deps_uri_0 = me.get_upload_uri(task_group_metadata, "deps-0")
    mock_cb_uri_0 = me.get_upload_uri(task_group_metadata, "call_before-0")
    mock_ca_uri_0 = me.get_upload_uri(task_group_metadata, "call_after-0")

    mock_function_uri_3 = me.get_upload_uri(task_group_metadata, "function-3")
    mock_deps_uri_3 = me.get_upload_uri(task_group_metadata, "deps-3")
    mock_cb_uri_3 = me.get_upload_uri(task_group_metadata, "call_before-3")
    mock_ca_uri_3 = me.get_upload_uri(task_group_metadata, "call_after-3")

    mock_node_upload_uri_1 = me.get_upload_uri(task_group_metadata, "node_1")
    mock_node_upload_uri_2 = me.get_upload_uri(task_group_metadata, "node_2")

    mock_function_id_0 = 0
    mock_args_ids = abstract_inputs["args"]
    mock_kwargs_ids = abstract_inputs["kwargs"]
    mock_deps_id_0 = "deps-0"
    mock_cb_id_0 = "call_before-0"
    mock_ca_id_0 = "call_after-0"

    mock_function_id_3 = 3
    mock_deps_id_3 = "deps-3"
    mock_cb_id_3 = "call_before-3"
    mock_ca_id_3 = "call_after-3"

    resources = {
        "functions": {
            0: mock_function_uri_0,
            3: mock_function_uri_3,
        },
        "inputs": {
            1: mock_node_upload_uri_1,
            2: mock_node_upload_uri_2,
        },
        "deps": {
            mock_deps_id_0: mock_deps_uri_0,
            mock_cb_id_0: mock_cb_uri_0,
            mock_ca_id_0: mock_ca_uri_0,
            mock_deps_id_3: mock_deps_uri_3,
            mock_cb_id_3: mock_cb_uri_3,
            mock_ca_id_3: mock_ca_uri_3,
        },
    }

    mock_task_spec_0 = {
        "function_id": mock_function_id_0,
        "args_ids": mock_args_ids,
        "kwargs_ids": mock_kwargs_ids,
        "deps_id": mock_deps_id_0,
        "call_before_id": mock_cb_id_0,
        "call_after_id": mock_ca_id_0,
    }

    mock_task_spec_3 = {
        "function_id": mock_function_id_3,
        "args_ids": mock_args_ids,
        "kwargs_ids": mock_kwargs_ids,
        "deps_id": mock_deps_id_3,
        "call_before_id": mock_cb_id_3,
        "call_after_id": mock_ca_id_3,
    }

    mock_task_0 = {
        "function_id": mock_function_id_0,
        "args_ids": mock_args_ids,
        "kwargs_ids": mock_kwargs_ids,
    }

    mock_task_3 = {
        "function_id": mock_function_id_3,
        "args_ids": mock_args_ids,
        "kwargs_ids": mock_kwargs_ids,
    }

    known_nodes = [1, 2]

    await _submit_abstract_task_group(
        dispatch_id=dispatch_id,
        task_group_id=0,
        task_seq=[mock_task_0, mock_task_3],
        known_nodes=known_nodes,
        executor=me,
    )

    mock_upload.assert_awaited()

    me.send.assert_awaited_with(
        [mock_task_spec_0, mock_task_spec_3],
        resources,
        task_group_metadata,
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
    mock_function_id = task_id
    mock_args_ids = abstract_inputs["args"]
    mock_kwargs_ids = abstract_inputs["kwargs"]

    mock_task = {
        "function_id": mock_function_id,
        "args_ids": mock_args_ids,
        "kwargs_ids": mock_kwargs_ids,
    }
    known_nodes = [1, 2]

    assert [node_result] == await _submit_abstract_task_group(
        dispatch_id, task_id, [mock_task], known_nodes, me
    )


@pytest.mark.asyncio
async def test_get_task_result(mocker):

    import datetime

    me = MockManagedExecutor()
    asset_uri = "file:///tmp/asset.pkl"
    mock_task_result = {
        "dispatch_id": "dispatch",
        "node_id": 0,
        "output_uri": asset_uri,
        "stdout_uri": asset_uri,
        "stderr_uri": asset_uri,
        "status": False,
    }
    me.receive = AsyncMock(return_value=[mock_task_result])

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
        "covalent_dispatcher._core.runner_exp.datamgr.update_node_result",
    )

    mock_upload = mocker.patch(
        "covalent_dispatcher._core.data_modules.asset_manager.upload_asset_for_nodes",
    )

    dispatch_id = "dispatch"
    task_id = 0
    name = "task"

    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "task_ids": [task_id],
        "task_group_id": task_id,
    }
    mock_job_handles = {(dispatch_id, task_id): 42}

    mocker.patch("covalent_dispatcher._core.runner_exp._job_handles", mock_job_handles)

    await _get_task_result(task_group_metadata)

    me.receive.assert_awaited_with(task_group_metadata, 42)

    mock_update.assert_awaited_with(dispatch_id, expected_node_result)

    # Test exception during get
    me.receive = AsyncMock(side_effect=RuntimeError())
    mock_update.reset_mock()

    await _get_task_result(task_group_metadata)
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
    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "task_ids": [task_id],
        "task_group_id": task_id,
    }

    mock_job_handles = {(dispatch_id, task_id): 42}

    mocker.patch("covalent_dispatcher._core.runner_exp._job_handles", mock_job_handles)

    await _poll_task_status(task_group_metadata, me)

    mock_mark_ready.assert_awaited()

    me.poll = AsyncMock(return_value=-1)
    mock_mark_ready.reset_mock()

    await _poll_task_status(task_group_metadata, me)
    mock_mark_ready.assert_not_awaited()

    me.poll = AsyncMock(side_effect=RuntimeError())
    mock_mark_ready.reset_mock()
    mock_mark_failed = mocker.patch(
        "covalent_dispatcher._core.runner_exp._mark_failed",
    )

    await _poll_task_status(task_group_metadata, me)
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
        "covalent_dispatcher._core.runner_exp.datamgr.update_node_result",
    )

    mock_get = mocker.patch("covalent_dispatcher._core.runner_exp._get_task_result")

    task_group_metadata = {"dispatch_id": "dispatch", "task_group_id": 1, "task_ids": [1]}

    job_events = [{"event": "READY", "task_group_metadata": task_group_metadata}, {"event": "BYE"}]

    mock_event_queue = asyncio.Queue()

    mocker.patch(
        "covalent_dispatcher._core.runner_exp._job_events",
        mock_event_queue,
    )
    fut = asyncio.create_task(_listen_for_job_events())
    await _mark_ready(task_group_metadata)
    await _mark_ready(task_group_metadata)
    await mock_event_queue.put({"event": "BYE"})

    await asyncio.wait_for(fut, 1)

    assert mock_get.call_count == 2

    mock_get.reset_mock()

    fut = asyncio.create_task(_listen_for_job_events())

    await _mark_failed(task_group_metadata, "error")
    await mock_event_queue.put({"event": "BYE"})

    await asyncio.wait_for(fut, 1)

    mock_update.assert_awaited_with(task_group_metadata["dispatch_id"], node_result)

    await mock_event_queue.put({"BAD_EVENT": "asdf"})
    await mock_event_queue.put({"event": "BYE"})
    mock_log = mocker.patch("covalent_dispatcher._core.runner_exp.app_log.exception")

    fut = asyncio.create_task(_listen_for_job_events())

    await _mark_failed(task_group_metadata, "error")
    await mock_event_queue.put({"event": "BYE"})

    await asyncio.wait_for(fut, 1)


@pytest.mark.asyncio
async def test_run_abstract_task_group(mocker):
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
        "covalent_dispatcher._core.runner_exp._submit_abstract_task_group",
        return_value=[node_result],
    )

    mock_update = mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.update_node_result",
    )

    dispatch_id = "dispatch"
    node_id = 0
    node_name = "task"
    abstract_inputs = {"args": [], "kwargs": {}}
    selected_executor = ["local", {}]
    mock_function_id = node_id
    mock_args_ids = abstract_inputs["args"]
    mock_kwargs_ids = abstract_inputs["kwargs"]

    mock_task = {
        "function_id": mock_function_id,
        "args_ids": mock_args_ids,
        "kwargs_ids": mock_kwargs_ids,
    }
    known_nodes = [1, 2]

    await run_abstract_task_group(
        dispatch_id,
        node_id,
        [mock_task],
        known_nodes,
        selected_executor,
    )

    mock_submit.assert_awaited()
    mock_update.assert_awaited()
    mock_poll.assert_awaited()


@pytest.mark.asyncio
async def test_run_abstract_task_group_handles_old_execs(mocker):
    mock_listen = AsyncMock()
    me = MockExecutor()
    mocker.patch(
        "covalent_dispatcher._core.runner_exp.get_executor",
        return_value=me,
    )

    mock_legacy_run = mocker.patch("covalent_dispatcher._core.runner.run_abstract_task")

    mock_submit = mocker.patch("covalent_dispatcher._core.runner_exp._submit_abstract_task_group")

    dispatch_id = "dispatch"
    node_id = 0
    node_name = "task"
    abstract_inputs = {"args": [], "kwargs": {}}
    selected_executor = ["local", {}]
    mock_function_id = node_id
    mock_args_ids = abstract_inputs["args"]
    mock_kwargs_ids = abstract_inputs["kwargs"]

    mock_task = {
        "function_id": mock_function_id,
        "name": node_name,
        "args_ids": mock_args_ids,
        "kwargs_ids": mock_kwargs_ids,
    }
    known_nodes = [1, 2]

    await run_abstract_task_group(
        dispatch_id,
        node_id,
        [mock_task],
        known_nodes,
        selected_executor,
    )

    mock_legacy_run.assert_called()
    mock_submit.assert_not_awaited()


@pytest.mark.asyncio
async def test_run_abstract_task_group_handles_bad_executors(mocker):
    """Check handling of executors during get_executor"""

    from covalent._shared_files.defaults import sublattice_prefix

    mocker.patch("covalent_dispatcher._core.runner_exp.get_executor", side_effect=RuntimeError())

    mock_update = mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.update_node_result",
    )
    dispatch_id = "dispatch"
    node_id = 0
    node_name = sublattice_prefix
    abstract_inputs = {"args": [], "kwargs": {}}
    selected_executor = ["local", {}]
    mock_function_id = node_id
    mock_args_ids = abstract_inputs["args"]
    mock_kwargs_ids = abstract_inputs["kwargs"]

    mock_task = {
        "function_id": mock_function_id,
        "args_ids": mock_args_ids,
        "kwargs_ids": mock_kwargs_ids,
    }
    known_nodes = [1, 2]

    await run_abstract_task_group(
        dispatch_id,
        node_id,
        [mock_task],
        known_nodes,
        selected_executor,
    )

    mock_update.assert_awaited()
