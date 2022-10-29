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


from unittest.mock import AsyncMock

import pytest

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.result import (
    _register_result_object,
    _registered_dispatches,
    _update_node_result,
    get_result_object,
    initialize_result_object,
    make_dispatch,
    unregister_dispatch,
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


@pytest.mark.asyncio
async def test_update_failed_node(mocker):
    """Check that update_node_result correctly invokes _handle_failed_node"""

    status_queue = AsyncMock()

    pending_deps = {}

    result_object = get_mock_result()
    mock_fail_handler = mocker.patch("covalent_dispatcher._core.dispatcher._handle_failed_node")
    mock_upsert_lattice = mocker.patch("covalent_dispatcher._db.upsert._lattice_data")
    mock_update_node = mocker.patch("covalent_dispatcher._db.update._node")

    node_result = {"node_id": 0, "status": Result.FAILED}
    await _update_node_result(result_object, node_result, pending_deps, status_queue)

    status_queue.put.assert_awaited_with((0, Result.FAILED))


@pytest.mark.asyncio
async def test_update_cancelled_node(mocker):
    """Check that update_node_result correctly invokes _handle_cancelled_node"""

    status_queue = AsyncMock()

    pending_deps = {}

    result_object = get_mock_result()
    mock_cancel_handler = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_cancelled_node"
    )
    mock_upsert_lattice = mocker.patch("covalent_dispatcher._db.upsert._lattice_data")
    mock_update_node = mocker.patch("covalent_dispatcher._db.update._node")

    node_result = {"node_id": 0, "status": Result.CANCELLED}
    await _update_node_result(result_object, node_result, pending_deps, status_queue)
    status_queue.put.assert_awaited_with((0, Result.CANCELLED))


@pytest.mark.asyncio
async def test_update_completed_node(mocker):
    """Check that update_node_result correctly invokes _handle_completed_node"""

    status_queue = AsyncMock()
    pending_deps = {}

    result_object = get_mock_result()
    mock_completed_handler = mocker.patch(
        "covalent_dispatcher._core.dispatcher._handle_completed_node"
    )
    mock_upsert_lattice = mocker.patch("covalent_dispatcher._db.upsert._lattice_data")
    mock_update_node = mocker.patch("covalent_dispatcher._db.update._node")

    node_result = {"node_id": 0, "status": Result.COMPLETED}
    await _update_node_result(result_object, node_result, pending_deps, status_queue)
    status_queue.put.assert_awaited_with((0, Result.COMPLETED))


def test_make_dispatch(mocker):
    res = get_mock_result()
    mock_init_result = mocker.patch(
        "covalent_dispatcher._core.result.initialize_result_object", return_value=res
    )
    mock_register = mocker.patch(
        "covalent_dispatcher._core.result._register_result_object", return_value=res
    )
    json_lattice = '{"workflow_function": "asdf"}'
    dispatch_id = make_dispatch(json_lattice)

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
    dispatch_id = result_object.dispatch_id
    _register_result_object(result_object)
    assert _registered_dispatches[dispatch_id] is result_object
    del _registered_dispatches[dispatch_id]


def test_unregister_result_object(mocker):
    result_object = get_mock_result()
    dispatch_id = result_object.dispatch_id
    _registered_dispatches[dispatch_id] = result_object
    unregister_dispatch(dispatch_id)
    assert dispatch_id not in _registered_dispatches
