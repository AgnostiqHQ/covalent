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


from unittest.mock import AsyncMock, MagicMock

import pytest

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.data_manager import (
    _dispatch_status_queues,
    _register_result_object,
    _registered_dispatches,
    _update_parent_electron,
    finalize_dispatch,
    get_result_object,
    get_status_queue,
    initialize_result_object,
    make_dispatch,
    persist_result,
    update_node_result,
    update_node_result_refs,
    upsert_lattice_data,
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


def test_initialize_result_object(mocker, test_db):
    """Test the `initialize_result_object` function"""

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph(1)
    json_lattice = workflow.serialize_to_json()
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", return_value=test_db)
    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", return_value=test_db)
    result_object = get_mock_result()

    mock_persist = mocker.patch("covalent_dispatcher._db.update.persist")

    sub_result_object = initialize_result_object(
        json_lattice=json_lattice, parent_result_object=result_object, parent_electron_id=5
    )

    mock_persist.assert_called_with(sub_result_object, electron_id=5)
    assert sub_result_object._root_dispatch_id == result_object.dispatch_id


@pytest.mark.parametrize("node_status", [Result.COMPLETED, Result.FAILED, Result.CANCELLED])
@pytest.mark.asyncio
async def test_update_node_result(mocker, node_status):
    """Check that update_node_result pushes the correct status updates"""

    status_queue = AsyncMock()

    result_object = get_mock_result()
    mock_update_node = mocker.patch("covalent_dispatcher._dal.result.Result._update_node")
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_status_queue", return_value=status_queue
    )
    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object", return_value=result_object
    )

    node_result = {"node_id": 0, "status": node_status}
    await update_node_result(result_object.dispatch_id, node_result)
    status_queue.put.assert_awaited_with((0, node_status))


@pytest.mark.asyncio
async def test_update_node_result_handles_db_exceptions(mocker):
    """Check that update_node_result handles db write failures"""

    status_queue = AsyncMock()

    result_object = get_mock_result()
    result_object._update_node = MagicMock(side_effect=RuntimeError())
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_status_queue", return_value=status_queue
    )
    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object", return_value=result_object
    )

    node_result = {"node_id": 0, "status": Result.COMPLETED}
    await update_node_result(result_object.dispatch_id, node_result)

    status_queue.put.assert_awaited_with((0, Result.FAILED))


@pytest.mark.asyncio
async def test_make_dispatch(mocker):
    res = get_mock_result()
    mock_init_result = mocker.patch(
        "covalent_dispatcher._core.data_manager.initialize_result_object", return_value=res
    )
    mock_register = mocker.patch(
        "covalent_dispatcher._core.data_manager._register_result_object", return_value=res
    )
    json_lattice = '{"workflow_function": "asdf"}'
    dispatch_id = await make_dispatch(json_lattice)

    assert dispatch_id == res.dispatch_id
    mock_register.assert_called_with(res)


def test_get_result_object(mocker):
    result_object = get_mock_result()
    dispatch_id = result_object.dispatch_id
    _registered_dispatches[dispatch_id] = result_object
    assert get_result_object(dispatch_id) is result_object
    del _registered_dispatches[dispatch_id]


def test_register_result_object(mocker):
    result_object = get_mock_result()
    srvres_obj = MagicMock()
    dispatch_id = result_object.dispatch_id
    mock_get_res_from_db = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object_from_db", return_value=srvres_obj
    )
    _register_result_object(result_object)
    assert _registered_dispatches[dispatch_id] is srvres_obj
    del _registered_dispatches[dispatch_id]


def test_unregister_result_object(mocker):
    result_object = get_mock_result()
    dispatch_id = result_object.dispatch_id
    _registered_dispatches[dispatch_id] = result_object
    finalize_dispatch(dispatch_id)
    assert dispatch_id not in _registered_dispatches


def test_get_status_queue():
    import asyncio

    dispatch_id = "dispatch"
    q = asyncio.Queue()
    _dispatch_status_queues[dispatch_id] = q
    assert get_status_queue(dispatch_id) is q


@pytest.mark.asyncio
async def test_persist_result(mocker):
    result_object = MagicMock()

    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object", return_value=result_object
    )
    mock_update_parent = mocker.patch(
        "covalent_dispatcher._core.data_manager._update_parent_electron"
    )

    await persist_result(result_object.dispatch_id)
    mock_update_parent.assert_awaited_with(result_object)


@pytest.mark.parametrize(
    "sub_status,mapped_status",
    [(Result.COMPLETED, Result.COMPLETED), (Result.POSTPROCESSING_FAILED, Result.FAILED)],
)
@pytest.mark.asyncio
async def test_update_parent_electron(mocker, sub_status, mapped_status):
    import datetime

    mock_res = get_mock_result()
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
        "covalent_dispatcher._core.data_manager.get_result_object",
        return_value=parent_result_obj,
    )

    await _update_parent_electron(sub_result_obj)

    mock_get_res.assert_called_with(parent_dispatch_id)
    mock_update_node.assert_awaited_with(parent_result_obj.dispatch_id, mock_node_result)


def test_upsert_lattice_data(mocker):
    result_object = get_mock_result()
    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object", return_value=result_object
    )
    mock_upsert_lattice = mocker.patch("covalent_dispatcher._db.upsert._lattice_data")
    upsert_lattice_data(result_object.dispatch_id)
    mock_upsert_lattice.assert_called_with(result_object)


@pytest.mark.asyncio
async def test_update_node_result_refs(mocker):
    mock_download = mocker.patch(
        "covalent_dispatcher._core.data_manager.am.download_assets_for_node"
    )

    stdout_uri = "file:///tmp/stdout.txt"
    stderr_uri = "file:///tmp/stderr.txt"
    output_uri = "file:///tmp/output/pkl"
    node_result = {
        "node_id": 2,
        "stdout_uri": stdout_uri,
        "stderr_uri": stderr_uri,
        "output_uri": output_uri,
    }

    src_uris = {"stdout": stdout_uri, "stderr": stderr_uri, "output": output_uri}
    mock_update = mocker.patch("covalent_dispatcher._core.data_manager.update_node_result")

    dispatch_id = "dispatch"

    await update_node_result_refs(dispatch_id, node_result)

    mock_download.assert_awaited_with(dispatch_id, 2, src_uris)
    mock_update.assert_awaited_with(dispatch_id, {"node_id": 2})


@pytest.mark.asyncio
async def test_update_node_result_refs_handles_failed_download(mocker):
    from covalent._shared_files.util_classes import RESULT_STATUS

    mock_download = mocker.patch(
        "covalent_dispatcher._core.data_manager.am.download_assets_for_node",
        side_effect=RuntimeError(),
    )
    stdout_uri = "file:///tmp/stdout.txt"
    stderr_uri = "file:///tmp/stderr.txt"
    output_uri = "file:///tmp/output/pkl"
    node_result = {
        "node_id": 2,
        "stdout_uri": stdout_uri,
        "stderr_uri": stderr_uri,
        "output_uri": output_uri,
    }

    src_uris = {"stdout": stdout_uri, "stderr": stderr_uri, "output": output_uri}
    mock_update = mocker.patch("covalent_dispatcher._core.data_manager.update_node_result")

    dispatch_id = "dispatch"

    await update_node_result_refs(dispatch_id, node_result)

    mock_update.assert_awaited_with(dispatch_id, {"node_id": 2, "status": RESULT_STATUS.FAILED})
