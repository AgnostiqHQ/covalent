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
Tests for the core functionality of the dispatcher.
"""


import base64
import tempfile
from unittest.mock import MagicMock

import pytest

import covalent as ct
from covalent._dispatcher_plugins.local import LocalDispatcher, pack_staging_dir
from covalent._results_manager import Result
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.data_manager import (
    _make_sublattice_dispatch,
    _update_parent_electron,
    ensure_dispatch,
    finalize_dispatch,
    get_result_object,
    persist_result,
    update_node_result,
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


@pytest.mark.parametrize(
    "node_status,node_type,output_status,sub_id",
    [
        (Result.COMPLETED, "function", Result.COMPLETED, ""),
        (Result.FAILED, "function", Result.FAILED, ""),
        (Result.CANCELLED, "function", Result.CANCELLED, ""),
        (Result.COMPLETED, "sublattice", RESULT_STATUS.DISPATCHING, ""),
        (Result.COMPLETED, "sublattice", RESULT_STATUS.DISPATCHING, "asdf"),
        (Result.COMPLETED, "sublattice", RESULT_STATUS.COMPLETED, "asdf"),
        (Result.FAILED, "sublattice", Result.FAILED, ""),
        (Result.CANCELLED, "sublattice", Result.CANCELLED, ""),
    ],
)
@pytest.mark.asyncio
async def test_update_node_result(mocker, node_status, node_type, output_status, sub_id):
    """Check that update_node_result pushes the correct status updates"""

    result_object = MagicMock()
    result_object.dispatch_id = "test_update_node_result"

    node_result = {"node_id": 0, "status": node_status}
    node_info = {"type": node_type, "sub_dispatch_id": sub_id, "status": Result.NEW_OBJ}
    subdispatch_info = (
        {"status": Result.NEW_OBJ}
        if output_status == RESULT_STATUS.DISPATCHING
        else {"status": Result.RUNNING}
    )
    mocker.patch("covalent_dispatcher._core.data_manager.electron.get", return_value=node_info)
    mocker.patch(
        "covalent_dispatcher._core.data_manager.dispatch.get", return_value=subdispatch_info
    )

    mock_notify = mocker.patch(
        "covalent_dispatcher._core.dispatcher.notify_node_status",
    )

    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.data_modules.electron.get_result_object",
        return_value=result_object,
    )

    mock_make_dispatch = mocker.patch(
        "covalent_dispatcher._core.data_manager._make_sublattice_dispatch",
        return_value=sub_id,
    )

    await update_node_result(result_object.dispatch_id, node_result)
    detail = {"sub_dispatch_id": sub_id} if sub_id else {}
    mock_notify.assert_awaited_with(result_object.dispatch_id, 0, output_status, detail)

    if node_status == Result.COMPLETED and node_type == "sublattice" and not sub_id:
        mock_make_dispatch.assert_awaited()
    else:
        mock_make_dispatch.assert_not_awaited()


@pytest.mark.parametrize(
    "node_status,old_status,valid_update",
    [
        (Result.COMPLETED, Result.RUNNING, True),
        (Result.COMPLETED, Result.COMPLETED, False),
        (Result.FAILED, Result.COMPLETED, False),
    ],
)
@pytest.mark.asyncio
async def test_update_node_result_filters_illegal_updates(
    mocker, node_status, old_status, valid_update
):
    """Check that update_node_result pushes the correct status updates"""

    result_object = MagicMock()
    result_object.dispatch_id = "test_update_node_result_filters_illegal_updates"
    result_object._update_node = MagicMock(return_value=valid_update)
    node_result = {"node_id": 0, "status": node_status}
    node_info = {"type": "function", "sub_dispatch_id": "", "status": old_status}
    mocker.patch("covalent_dispatcher._core.data_manager.electron.get", return_value=node_info)

    mock_notify = mocker.patch(
        "covalent_dispatcher._core.dispatcher.notify_node_status",
    )

    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.data_modules.electron.get_result_object",
        return_value=result_object,
    )

    mocker.patch(
        "covalent_dispatcher._core.data_manager._make_sublattice_dispatch",
    )

    await update_node_result(result_object.dispatch_id, node_result)

    if not valid_update:
        mock_notify.assert_not_awaited()
    else:
        mock_notify.assert_awaited()


@pytest.mark.asyncio
async def test_update_node_result_handles_keyerrors(mocker):
    """Check that update_node_result handles invalid dispatch id or node id"""

    result_object = MagicMock()
    result_object.dispatch_id = "test_update_node_result_handles_keyerrors"
    node_result = {"node_id": -5, "status": RESULT_STATUS.COMPLETED}
    mock_update_node = mocker.patch("covalent_dispatcher._dal.result.Result._update_node")
    node_info = {"type": "function", "sub_dispatch_id": "", "status": RESULT_STATUS.RUNNING}
    mocker.patch("covalent_dispatcher._core.data_manager.electron.get", side_effect=KeyError())

    mock_notify = mocker.patch(
        "covalent_dispatcher._core.dispatcher.notify_node_status",
    )

    await update_node_result(result_object.dispatch_id, node_result)

    mock_notify.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_node_result_handles_subl_exceptions(mocker):
    """Check that update_node_result pushes the correct status updates"""

    result_object = MagicMock()
    result_object.dispatch_id = "test_update_node_result_handles_subl_exception"

    node_type = "sublattice"
    sub_id = ""
    node_result = {"node_id": 0, "status": Result.COMPLETED}
    mock_update_node = mocker.patch("covalent_dispatcher._dal.result.Result._update_node")
    node_info = {"type": node_type, "sub_dispatch_id": sub_id, "status": Result.NEW_OBJ}
    mocker.patch("covalent_dispatcher._core.data_manager.electron.get", return_value=node_info)
    mock_notify = mocker.patch(
        "covalent_dispatcher._core.dispatcher.notify_node_status",
    )

    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.data_modules.electron.get_result_object",
        return_value=result_object,
    )

    mock_make_dispatch = mocker.patch(
        "covalent_dispatcher._core.data_manager._make_sublattice_dispatch",
        side_effect=RuntimeError(),
    )

    mocker.patch("traceback.TracebackException.from_exception", return_value="error")

    await update_node_result(result_object.dispatch_id, node_result)
    output_status = Result.FAILED
    mock_notify.assert_awaited_with(result_object.dispatch_id, 0, output_status, {})
    mock_make_dispatch.assert_awaited()


@pytest.mark.asyncio
async def test_update_node_result_handles_db_exceptions(mocker):
    """Check that update_node_result handles db write failures"""

    result_object = MagicMock()
    result_object.dispatch_id = "test_update_node_result_handles_db_exceptions"
    result_object._update_node = MagicMock(side_effect=RuntimeError())
    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.data_modules.electron.get_result_object",
        return_value=result_object,
    )
    mock_notify = mocker.patch(
        "covalent_dispatcher._core.dispatcher.notify_node_status",
    )

    node_result = {"node_id": 0, "status": Result.COMPLETED}
    await update_node_result(result_object.dispatch_id, node_result)

    mock_notify.assert_awaited_with(result_object.dispatch_id, 0, Result.FAILED, {})


def test_get_result_object(mocker):
    result_object = MagicMock()
    result_object.dispatch_id = "dispatch_1"
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object_from_db",
        return_value=result_object,
    )

    dispatch_id = result_object.dispatch_id
    assert get_result_object(dispatch_id) is result_object


@pytest.mark.parametrize("stateless", [False, True])
def test_unregister_result_object(mocker, stateless):
    dispatch_id = "test_unregister_result_object"
    finalize_dispatch(dispatch_id)


@pytest.mark.asyncio
async def test_persist_result(mocker):
    dispatch_id = "test_persist_result"
    mock_update_parent = mocker.patch(
        "covalent_dispatcher._core.data_manager._update_parent_electron"
    )

    await persist_result(dispatch_id)
    mock_update_parent.assert_awaited_with(dispatch_id)


@pytest.mark.parametrize(
    "sub_status,mapped_status",
    [(Result.COMPLETED, Result.COMPLETED), (Result.POSTPROCESSING_FAILED, Result.FAILED)],
)
@pytest.mark.asyncio
async def test_update_parent_electron(mocker, sub_status, mapped_status):
    import datetime

    mock_res = MagicMock()
    mock_res.dispatch_id = "test_update_parent_electron"
    parent_result_obj = MagicMock()
    sub_result_obj = MagicMock()
    eid = 5

    parent_result_obj.dispatch_id = mock_res.dispatch_id

    parent_dispatch_id = (parent_result_obj.dispatch_id,)
    parent_node_id = 2
    sub_result_obj._electron_id = eid
    sub_result_obj.status = sub_status
    sub_result_obj._result = 42
    sub_result_obj._error = ""
    sub_result_obj._end_time = datetime.datetime.now()

    mock_node_result = {
        "node_id": parent_node_id,
        "end_time": sub_result_obj._end_time,
        "status": mapped_status,
        "output": sub_result_obj._result,
        "error": sub_result_obj._error,
    }

    mock_gen_node_result = mocker.patch(
        "covalent_dispatcher._core.data_manager.generate_node_result",
        return_value=mock_node_result,
    )

    mock_update_node = mocker.patch("covalent_dispatcher._core.data_manager.update_node_result")
    mock_resolve_eid = mocker.patch(
        "covalent_dispatcher._core.data_manager.resolve_electron_id",
        return_value=(parent_dispatch_id, parent_node_id),
    )
    mock_get_res = mocker.patch(
        "covalent_dispatcher._core.data_modules.dispatch.get_result_object",
        return_value=parent_result_obj,
    )

    mock_get_res = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object",
        return_value=parent_result_obj,
    )

    await _update_parent_electron(sub_result_obj)

    mock_get_res.assert_called_with(parent_dispatch_id)
    mock_update_node.assert_awaited_with(parent_result_obj.dispatch_id, mock_node_result)


@pytest.mark.asyncio
async def test_make_sublattice_dispatch(mocker):

    @ct.lattice
    @ct.electron
    def sublattice(x):
        return x**2

    sublattice.build_graph(3)

    with tempfile.TemporaryDirectory(prefix="covalent-") as staging_path:
        manifest = LocalDispatcher.prepare_manifest(sublattice, staging_path)

        # This tarball will be unpacked and resubmitted server-side
        tar_file = pack_staging_dir(staging_path, manifest)
        with open(tar_file, "rb") as tar:
            tar_b64 = base64.b64encode(tar.read()).decode("utf-8")

    # This base64-encoded tarball will be read server-side
    # as `TransportableObject.object_string`

    node_result = {"node_id": 0, "status": Result.COMPLETED}

    mock_node = MagicMock()
    mock_node._electron_id = 5

    mock_bg_output = MagicMock()
    mock_bg_output.object_string = tar_b64

    mock_node.get_value = MagicMock(return_value=mock_bg_output)

    mock_manifest = MagicMock()
    mock_manifest.metadata.dispatch_id = "mock_sublattice_dispatch"

    result_object = MagicMock()
    result_object.dispatch_id = "dispatch"
    result_object.lattice.transport_graph.get_node = MagicMock(return_value=mock_node)
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object",
        return_value=result_object,
    )
    mocker.patch(
        "covalent_dispatcher._core.data_modules.importer._import_manifest",
        return_value=mock_manifest,
    )

    mock_pull = mocker.patch("covalent_dispatcher._core.data_modules.importer._pull_assets")
    sub_dispatch_id = await _make_sublattice_dispatch(result_object.dispatch_id, node_result)
    mock_pull.assert_called()

    assert sub_dispatch_id == mock_manifest.metadata.dispatch_id


@pytest.mark.asyncio
async def test_ensure_dispatch(mocker):
    mock_ensure_run_once = mocker.patch(
        "covalent_dispatcher._core.data_manager.SRVResult.ensure_run_once",
        return_value=True,
    )
    assert await ensure_dispatch("test_ensure_dispatch") is True
    mock_ensure_run_once.assert_called_with("test_ensure_dispatch")
