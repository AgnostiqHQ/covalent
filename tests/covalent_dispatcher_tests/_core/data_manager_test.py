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


from unittest.mock import MagicMock

import pytest

import covalent as ct
from covalent._results_manager import Result
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.data_manager import (
    _get_result_object_from_new_lattice,
    _make_sublattice_dispatch,
    _register_result_object,
    _update_parent_electron,
    finalize_dispatch,
    get_result_object,
    initialize_result_object,
    make_derived_dispatch,
    make_dispatch,
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


@pytest.mark.parametrize(
    "node_status,node_type,output_status,sub_id",
    [
        (Result.COMPLETED, "function", Result.COMPLETED, ""),
        (Result.FAILED, "function", Result.FAILED, ""),
        (Result.CANCELLED, "function", Result.CANCELLED, ""),
        (Result.COMPLETED, "sublattice", RESULT_STATUS.DISPATCHING, ""),
        (Result.COMPLETED, "sublattice", RESULT_STATUS.COMPLETED, "asdf"),
        (Result.FAILED, "sublattice", Result.FAILED, ""),
        (Result.CANCELLED, "sublattice", Result.CANCELLED, ""),
    ],
)
@pytest.mark.asyncio
async def test_update_node_result(mocker, node_status, node_type, output_status, sub_id):
    """Check that update_node_result pushes the correct status updates"""

    result_object = get_mock_result()
    node_result = {"node_id": 0, "status": node_status}
    mock_update_node = mocker.patch("covalent_dispatcher._dal.result.Result._update_node")
    node_info = {"type": node_type, "sub_dispatch_id": sub_id, "status": Result.NEW_OBJ}
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_electron_attributes", return_value=node_info
    )

    mock_notify = mocker.patch(
        "covalent_dispatcher._core.dispatcher.notify_node_status",
    )

    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object", return_value=result_object
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
    "node_status,old_status",
    [
        (Result.COMPLETED, Result.RUNNING),
        (Result.COMPLETED, Result.COMPLETED),
        (Result.FAILED, Result.COMPLETED),
    ],
)
@pytest.mark.asyncio
async def test_update_node_result_filters_illegal_updates(mocker, node_status, old_status):
    """Check that update_node_result pushes the correct status updates"""

    result_object = get_mock_result()
    node_result = {"node_id": 0, "status": node_status}
    mock_update_node = mocker.patch("covalent_dispatcher._dal.result.Result._update_node")
    node_info = {"type": "function", "sub_dispatch_id": "", "status": old_status}
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_electron_attributes", return_value=node_info
    )

    mock_notify = mocker.patch(
        "covalent_dispatcher._core.dispatcher.notify_node_status",
    )

    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object", return_value=result_object
    )

    mocker.patch(
        "covalent_dispatcher._core.data_manager._make_sublattice_dispatch",
    )

    await update_node_result(result_object.dispatch_id, node_result)

    if old_status == node_status or RESULT_STATUS.is_terminal(old_status):
        mock_notify.assert_not_awaited()
    else:
        mock_notify.assert_awaited()


@pytest.mark.asyncio
async def test_update_node_result_handles_keyerrors(mocker):
    """Check that update_node_result handles invalid dispatch id or node id"""

    result_object = get_mock_result()
    node_result = {"node_id": -5, "status": RESULT_STATUS.COMPLETED}
    mock_update_node = mocker.patch("covalent_dispatcher._dal.result.Result._update_node")
    node_info = {"type": "function", "sub_dispatch_id": "", "status": RESULT_STATUS.RUNNING}
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_electron_attributes", side_effect=KeyError()
    )

    mock_notify = mocker.patch(
        "covalent_dispatcher._core.dispatcher.notify_node_status",
    )

    await update_node_result(result_object.dispatch_id, node_result)

    mock_notify.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_node_result_handles_subl_exceptions(mocker):
    """Check that update_node_result pushes the correct status updates"""

    result_object = get_mock_result()
    node_type = "sublattice"
    sub_id = ""
    node_result = {"node_id": 0, "status": Result.COMPLETED}
    mock_update_node = mocker.patch("covalent_dispatcher._dal.result.Result._update_node")
    node_info = {"type": node_type, "sub_dispatch_id": sub_id, "status": Result.NEW_OBJ}
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_electron_attributes", return_value=node_info
    )
    mock_notify = mocker.patch(
        "covalent_dispatcher._core.dispatcher.notify_node_status",
    )

    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object", return_value=result_object
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

    result_object = get_mock_result()
    result_object._update_node = MagicMock(side_effect=RuntimeError())
    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object", return_value=result_object
    )
    mock_notify = mocker.patch(
        "covalent_dispatcher._core.dispatcher.notify_node_status",
    )

    node_result = {"node_id": 0, "status": Result.COMPLETED}
    await update_node_result(result_object.dispatch_id, node_result)

    mock_notify.assert_awaited_with(result_object.dispatch_id, 0, Result.FAILED, {})


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


@pytest.mark.parametrize("reuse", [True, False])
def test_get_result_object_from_new_lattice(mocker, reuse):
    """Test the get result object from new lattice json function."""
    lattice_mock = mocker.patch("covalent_dispatcher._core.data_manager.Lattice")
    result_object_mock = mocker.patch("covalent_dispatcher._core.data_manager.Result")
    update_mock = mocker.patch("covalent_dispatcher._core.data_manager.update")
    old_result_mock = MagicMock()
    get_result_mock = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object_from_db",
        return_value=old_result_mock,
    )
    mock_get_reusable_nodes = MagicMock()
    mock_copy_nodes_from = MagicMock()
    mocker.patch(
        "covalent_dispatcher._dal.tg_ops.TransportGraphOps.get_reusable_nodes",
        mock_get_reusable_nodes,
    )
    mocker.patch(
        "covalent_dispatcher._dal.tg_ops.TransportGraphOps.copy_nodes_from",
        mock_copy_nodes_from,
    )

    res = _get_result_object_from_new_lattice(
        json_lattice="mock-lattice",
        old_result_object=old_result_mock,
        reuse_previous_results=reuse,
    )
    lattice_mock.deserialize_from_json.assert_called_with("mock-lattice")
    update_mock.persist.assert_called()

    if reuse:
        mock_get_reusable_nodes.assert_called()
        mock_copy_nodes_from.assert_called()

    else:
        mock_get_reusable_nodes.assert_not_called()
        mock_copy_nodes_from.assert_not_called()


@pytest.mark.parametrize("reuse", [True, False])
@pytest.mark.asyncio
async def test_make_derived_dispatch_from_lattice(mocker, reuse):
    """Test the make derived dispatch function."""

    def mock_func():
        pass

    mock_old_result = MagicMock()
    mock_new_result = MagicMock()
    mock_apply_electron_updates = MagicMock()
    mock_new_result.dispatch_id = "mock-redispatch-id"
    mock_new_result.lattice.transport_graph._graph.nodes = ["mock-nodes"]

    mocker.patch(
        "covalent_dispatcher._core.data_manager.export_serialized_result",
        return_value={"lattice": "lattice_json"},
    )
    get_result_mock = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object_from_db",
        return_value=mock_old_result,
    )
    get_result_object_from_new_lattice_mock = mocker.patch(
        "covalent_dispatcher._core.data_manager._get_result_object_from_new_lattice",
        return_value=mock_new_result,
    )

    register_result_object_mock = mocker.patch(
        "covalent_dispatcher._core.data_manager._register_result_object"
    )

    mocker.patch(
        "covalent_dispatcher._dal.tg_ops.TransportGraphOps.apply_electron_updates",
        mock_apply_electron_updates,
    )
    mock_electron_updates = {"mock-electron-id": mock_func}
    redispatch_id = await make_derived_dispatch(
        parent_dispatch_id="mock-dispatch-id",
        json_lattice="mock-json-lattice",
        electron_updates=mock_electron_updates,
        reuse_previous_results=reuse,
    )
    get_result_mock.called_once_with(dispatch_id="mock-dispatch-id", bare=False)

    get_result_object_from_new_lattice_mock.assert_called_once_with(
        "mock-json-lattice", mock_old_result, reuse
    )

    mock_apply_electron_updates.assert_called_once_with(mock_electron_updates)
    register_result_object_mock.assert_called_once_with(mock_new_result)
    assert redispatch_id == "mock-redispatch-id"


@pytest.mark.parametrize("reuse", [True, False])
@pytest.mark.asyncio
async def test_make_derived_dispatch_from_old_result(mocker, reuse):
    """Test the make derived dispatch function."""
    mock_old_result = MagicMock()
    mock_new_result = MagicMock()
    mock_apply_electron_updates = MagicMock()
    mock_new_result.dispatch_id = "mock-redispatch-id"
    mock_new_result.lattice.transport_graph._graph.nodes = ["mock-nodes"]

    get_result_mock = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object_from_db",
        return_value=mock_old_result,
    )
    mocker.patch(
        "covalent_dispatcher._core.data_manager.export_serialized_result",
        return_value={"lattice": "lattice_json"},
    )

    get_result_object_from_new_lattice_mock = mocker.patch(
        "covalent_dispatcher._core.data_manager._get_result_object_from_new_lattice",
        return_value=mock_new_result,
    )
    update_mock = mocker.patch("covalent_dispatcher._core.data_manager.update")
    register_result_object_mock = mocker.patch(
        "covalent_dispatcher._core.data_manager._register_result_object"
    )
    mocker.patch(
        "covalent_dispatcher._dal.tg_ops.TransportGraphOps.apply_electron_updates",
        mock_apply_electron_updates,
    )

    redispatch_id = await make_derived_dispatch(
        parent_dispatch_id="mock-dispatch-id",
        reuse_previous_results=reuse,
    )
    get_result_mock.called_once_with(dispatch_id="mock-dispatch-id", bare=False)
    get_result_object_from_new_lattice_mock.assert_called_once_with(
        "lattice_json", mock_old_result, reuse
    )

    mock_apply_electron_updates.assert_called_once_with({})
    update_mock().persist.called_once_with(mock_new_result)
    register_result_object_mock.assert_called_once_with(mock_new_result)
    assert redispatch_id == "mock-redispatch-id"


def test_get_result_object(mocker):
    result_object = MagicMock()
    result_object.dispatch_id = "dispatch_1"
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object_from_db",
        return_value=result_object,
    )

    dispatch_id = result_object.dispatch_id
    _registered_dispatches = {}
    mocker.patch(
        "covalent_dispatcher._core.data_manager._registered_dispatches",
        _registered_dispatches,
    )
    _registered_dispatches[dispatch_id] = result_object
    assert get_result_object(dispatch_id) is result_object


@pytest.mark.parametrize("stateless", [False, True])
def test_register_result_object(mocker, stateless):

    result_object = get_mock_result()
    srvres_obj = MagicMock()
    dispatch_id = result_object.dispatch_id
    mocker.patch(
        "covalent_dispatcher._core.data_manager.STATELESS",
        stateless,
    )
    mock_get_res_from_db = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object_from_db", return_value=srvres_obj
    )
    _registered_dispatches = {}
    mocker.patch(
        "covalent_dispatcher._core.data_manager._registered_dispatches",
        _registered_dispatches,
    )

    _register_result_object(result_object)
    if not stateless:
        assert _registered_dispatches[dispatch_id] is srvres_obj
        del _registered_dispatches[dispatch_id]
    else:
        assert dispatch_id not in _registered_dispatches


@pytest.mark.parametrize("stateless", [False, True])
def test_unregister_result_object(mocker, stateless):
    result_object = get_mock_result()
    dispatch_id = result_object.dispatch_id
    mocker.patch(
        "covalent_dispatcher._core.data_manager.STATELESS",
        stateless,
    )
    _registered_dispatches = {dispatch_id: result_object}
    mocker.patch(
        "covalent_dispatcher._core.data_manager._registered_dispatches",
        _registered_dispatches,
    )
    _registered_dispatches[dispatch_id] = result_object
    finalize_dispatch(dispatch_id)
    if not stateless:
        assert dispatch_id not in _registered_dispatches


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


@pytest.mark.asyncio
async def test_make_sublattice_dispatch(mocker):

    node_result = {"node_id": 0, "status": Result.COMPLETED}

    output_json = "lattice_json"
    mock_node = MagicMock()
    mock_node._electron_id = 5
    print("DEBUG:", mock_node)

    mock_bg_output = MagicMock()
    mock_bg_output.object_string = output_json

    result_object = MagicMock()
    result_object.dispatch_id = "dispatch"
    result_object.lattice.transport_graph.get_node = MagicMock(return_value=mock_node)
    print("DEBUG:", result_object.lattice.transport_graph.get_node())
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_electron_attribute",
        return_value=mock_bg_output,
    )
    mock_make_dispatch = mocker.patch("covalent_dispatcher._core.data_manager.make_dispatch")
    await _make_sublattice_dispatch(result_object, node_result)

    mock_make_dispatch.assert_awaited_with("lattice_json", result_object, mock_node._electron_id)
