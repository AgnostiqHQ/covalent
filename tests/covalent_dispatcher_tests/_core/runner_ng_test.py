# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tests for the core functionality of the runner.
"""


import asyncio
import datetime
import sys
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.pool import StaticPool

import covalent as ct
from covalent._results_manager import Result
from covalent._shared_files.exceptions import TaskCancelledError
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._workflow.lattice import Lattice
from covalent.executor.base import AsyncBaseExecutor
from covalent.executor.schemas import ResourceMap, TaskSpec, TaskUpdate
from covalent_dispatcher._core.runner_ng import (
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
@pytest.mark.parametrize(
    "task_cancelled",
    [False, True],
)
async def test_submit_abstract_task_group(mocker, task_cancelled):
    me = MockManagedExecutor()

    if task_cancelled:
        me.send = AsyncMock(side_effect=TaskCancelledError())
    else:
        me.send = AsyncMock(return_value="42")

    mocker.patch(
        "covalent_dispatcher._core.runner_ng.datamgr.electron.get",
        return_value={"executor": "managed_dask", "executor_data": {}},
    )

    mocker.patch(
        "covalent_dispatcher._core.runner_ng.get_executor",
        return_value=me,
    )

    ts = datetime.datetime.now()

    node_result = {
        "node_id": 0,
        "start_time": ts,
        "status": "RUNNING",
    }

    mocker.patch(
        "covalent_dispatcher._core.runner_ng.datamgr.generate_node_result",
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
        "node_ids": [0, 3],
        "task_group_id": 0,
    }

    mock_function_uri_0 = me.get_upload_uri(task_group_metadata, "function-0")
    mock_hooks_uri_0 = me.get_upload_uri(task_group_metadata, "hooks-0")

    mock_function_uri_3 = me.get_upload_uri(task_group_metadata, "function-3")
    mock_hooks_uri_3 = me.get_upload_uri(task_group_metadata, "hooks-3")

    mock_node_upload_uri_1 = me.get_upload_uri(task_group_metadata, "node_1")
    mock_node_upload_uri_2 = me.get_upload_uri(task_group_metadata, "node_2")

    mock_function_id_0 = 0
    mock_args_ids = abstract_inputs["args"]
    mock_kwargs_ids = abstract_inputs["kwargs"]

    mock_function_id_3 = 3

    resources = {
        "functions": {
            0: mock_function_uri_0,
            3: mock_function_uri_3,
        },
        "inputs": {
            1: mock_node_upload_uri_1,
            2: mock_node_upload_uri_2,
        },
        "hooks": {0: mock_hooks_uri_0, 3: mock_hooks_uri_3},
    }

    mock_task_spec_0 = {
        "function_id": mock_function_id_0,
        "args_ids": mock_args_ids,
        "kwargs_ids": mock_kwargs_ids,
    }

    mock_task_spec_3 = {
        "function_id": mock_function_id_3,
        "args_ids": mock_args_ids,
        "kwargs_ids": mock_kwargs_ids,
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

    node_result, send_retval = await _submit_abstract_task_group(
        dispatch_id=dispatch_id,
        task_group_id=0,
        task_seq=[mock_task_0, mock_task_3],
        known_nodes=known_nodes,
        executor=me,
    )

    mock_upload.assert_awaited()

    me.send.assert_awaited_with(
        [TaskSpec(**mock_task_spec_0), TaskSpec(**mock_task_spec_3)],
        ResourceMap(**resources),
        task_group_metadata,
    )

    if task_cancelled:
        assert send_retval is None
    else:
        assert send_retval == "42"


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
        "covalent_dispatcher._core.runner_ng.datamgr.electron.get",
        return_value={"executor": "managed_dask", "executor_data": {}},
    )

    mocker.patch(
        "covalent_dispatcher._core.runner_ng.get_executor",
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
        "covalent_dispatcher._core.runner_ng.datamgr.generate_node_result",
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

    assert ([node_result], None) == await _submit_abstract_task_group(
        dispatch_id, task_id, [mock_task], known_nodes, me
    )


@pytest.mark.asyncio
async def test_get_task_result(mocker):
    me = MockManagedExecutor()
    asset_uri = "file:///tmp/asset.pkl"
    mock_task_result = {
        "dispatch_id": "dispatch",
        "node_id": 0,
        "assets": {
            "output": {
                "remote_uri": asset_uri,
                "size": 0,
            },
            "stdout": {
                "remote_uri": asset_uri,
                "size": 0,
            },
            "stderr": {
                "remote_uri": asset_uri,
                "size": 0,
            },
        },
        "status": RESULT_STATUS.COMPLETED,
    }
    me.receive = AsyncMock(return_value=[TaskUpdate(**mock_task_result)])

    mocker.patch(
        "covalent_dispatcher._core.runner_ng.datamgr.electron.get",
        return_value={"executor": "managed_dask", "executor_data": {}},
    )

    mocker.patch(
        "covalent_dispatcher._core.runner_ng.get_executor",
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
    }

    mocker.patch(
        "covalent_dispatcher._core.runner_ng.datamgr.generate_node_result",
        return_value=node_result,
    )

    mock_update = mocker.patch(
        "covalent_dispatcher._core.runner_ng.datamgr.update_node_result",
    )
    mock_download = mocker.patch(
        "covalent_dispatcher._core.data_modules.asset_manager.download_assets_for_node",
    )

    dispatch_id = "dispatch"
    task_id = 0
    name = "task"

    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "node_ids": [task_id],
        "task_group_id": task_id,
    }
    job_meta = [{"job_handle": "42", "status": "COMPLETED"}]

    await _get_task_result(task_group_metadata, job_meta)

    me.receive.assert_awaited_with(task_group_metadata, job_meta)

    mock_update.assert_awaited_with(dispatch_id, expected_node_result)
    mock_download.assert_awaited()
    # Test exception during get
    me.receive = AsyncMock(side_effect=RuntimeError())
    mock_update.reset_mock()

    await _get_task_result(task_group_metadata, job_meta)
    mock_update.assert_awaited()


@pytest.mark.asyncio
async def test_poll_status(mocker):
    me = MockManagedExecutor()
    me.poll = AsyncMock(return_value=0)
    mocker.patch(
        "covalent_dispatcher._core.runner_ng.get_executor",
        return_value=me,
    )
    mock_mark_ready = mocker.patch(
        "covalent_dispatcher._core.runner_ng._mark_ready",
    )

    dispatch_id = "dispatch"
    task_id = 1
    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "node_ids": [task_id],
        "task_group_id": task_id,
    }

    await _poll_task_status(task_group_metadata, me, "42")

    mock_mark_ready.assert_awaited_with(task_group_metadata, 0)

    me.poll = AsyncMock(side_effect=NotImplementedError())
    mock_mark_ready.reset_mock()

    await _poll_task_status(task_group_metadata, me, "42")
    mock_mark_ready.assert_not_awaited()

    me.poll = AsyncMock(side_effect=RuntimeError())
    mock_mark_ready.reset_mock()
    mock_mark_failed = mocker.patch(
        "covalent_dispatcher._core.runner_ng._mark_failed",
    )

    await _poll_task_status(task_group_metadata, me, "42")
    mock_mark_ready.assert_not_awaited()
    mock_mark_failed.assert_awaited()
    mock_mark_ready.reset_mock()
    mock_mark_failed.reset_mock()

    me.poll = AsyncMock(side_effect=TaskCancelledError())

    await _poll_task_status(task_group_metadata, me, "42")
    mock_mark_ready.assert_awaited_with(task_group_metadata, None)
    mock_mark_failed.assert_not_awaited()


@pytest.mark.asyncio
async def test_event_listener(mocker):
    ts = datetime.datetime.now()
    node_result = {
        "node_id": 0,
        "start_time": ts,
        "end_time": ts,
        "status": RESULT_STATUS.FAILED,
        "error": "error",
    }

    mocker.patch(
        "covalent_dispatcher._core.runner_ng.datamgr.generate_node_result",
        return_value=node_result,
    )

    mock_update = mocker.patch(
        "covalent_dispatcher._core.runner_ng.datamgr.update_node_result",
    )

    mock_get = mocker.patch("covalent_dispatcher._core.runner_ng._get_task_result")

    task_group_metadata = {"dispatch_id": "dispatch", "task_group_id": 1, "node_ids": [1]}

    job_events = [{"event": "READY", "task_group_metadata": task_group_metadata}, {"event": "BYE"}]

    mock_event_queue = asyncio.Queue()

    mocker.patch(
        "covalent_dispatcher._core.runner_ng._job_events",
        mock_event_queue,
    )
    fut = asyncio.create_task(_listen_for_job_events())
    await _mark_ready(task_group_metadata, "RUNNING")
    await _mark_ready(task_group_metadata, "COMPLETED")
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
    mock_log = mocker.patch("covalent_dispatcher._core.runner_ng.app_log.exception")

    fut = asyncio.create_task(_listen_for_job_events())

    await _mark_failed(task_group_metadata, "error")
    await mock_event_queue.put({"event": "BYE"})

    await asyncio.wait_for(fut, 1)


@pytest.mark.asyncio
async def test_run_abstract_task_group(mocker):
    mock_listen = AsyncMock()
    me = MockManagedExecutor()
    me._init_runtime()

    me.poll = AsyncMock(return_value=0)
    mocker.patch(
        "covalent_dispatcher._core.runner_ng.get_executor",
        return_value=me,
    )

    mocker.patch(
        "covalent_dispatcher._core.runner_modules.jobs.get_cancel_requested", return_value=False
    )

    mock_poll = mocker.patch(
        "covalent_dispatcher._core.runner_ng._poll_task_status",
    )

    node_result = {"node_id": 0, "status": RESULT_STATUS.RUNNING}

    mock_submit = mocker.patch(
        "covalent_dispatcher._core.runner_ng._submit_abstract_task_group",
        return_value=([node_result], 42),
    )

    mock_update = mocker.patch(
        "covalent_dispatcher._core.runner_ng.datamgr.update_node_result",
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
    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "node_ids": [node_id],
        "task_group_id": node_id,
    }

    await run_abstract_task_group(
        dispatch_id,
        node_id,
        [mock_task],
        known_nodes,
        selected_executor,
    )

    mock_submit.assert_awaited()
    mock_update.assert_awaited()
    mock_poll.assert_awaited_with(task_group_metadata, me, 42)


@pytest.mark.asyncio
async def test_run_abstract_task_group_handles_old_execs(mocker):
    mock_listen = AsyncMock()
    me = MockExecutor()
    me._init_runtime()

    mocker.patch(
        "covalent_dispatcher._core.runner_ng.get_executor",
        return_value=me,
    )
    mocker.patch(
        "covalent_dispatcher._core.runner_modules.jobs.get_cancel_requested", return_value=False
    )

    mock_legacy_run = mocker.patch("covalent_dispatcher._core.runner.run_abstract_task")

    mock_submit = mocker.patch("covalent_dispatcher._core.runner_ng._submit_abstract_task_group")

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

    mocker.patch("covalent_dispatcher._core.runner_ng.get_executor", side_effect=RuntimeError())

    mock_update = mocker.patch(
        "covalent_dispatcher._core.runner_ng.datamgr.update_node_result",
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


@pytest.mark.asyncio
async def test_run_abstract_task_group_handles_cancelled_tasks(mocker):
    """Check handling of cancelled tasks"""

    mock_listen = AsyncMock()
    me = MockManagedExecutor()
    me._init_runtime()

    me.poll = AsyncMock(return_value=0)

    mocker.patch(
        "covalent_dispatcher._core.runner_modules.jobs.get_cancel_requested", return_value=True
    )

    mock_jobs_put = mocker.patch(
        "covalent_dispatcher._core.runner_modules.jobs.put_job_status", return_value=True
    )

    mock_submit = mocker.patch(
        "covalent_dispatcher._core.runner_ng._submit_abstract_task_group",
    )

    mock_update = mocker.patch(
        "covalent_dispatcher._core.runner_ng.datamgr.update_node_result",
    )
    mock_mark_ready = mocker.patch(
        "covalent_dispatcher._core.runner_ng.mark_task_ready",
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

    mock_submit.assert_not_awaited()
    mock_update.assert_not_awaited()
    mock_mark_ready.assert_awaited()
