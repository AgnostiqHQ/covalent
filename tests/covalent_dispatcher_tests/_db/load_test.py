# Copyright 2023 Agnostiq Inc.
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


"""Unit tests for result loading (from database) module."""

from unittest.mock import call

import pytest
from sqlalchemy import select

import covalent as ct
from covalent._results_manager.result import Result as SDKResult
from covalent._shared_files.util_classes import Status
from covalent._workflow.lattice import Lattice as SDKLattice
from covalent_dispatcher._db import models, update
from covalent_dispatcher._db.datastore import DataStore
from covalent_dispatcher._db.load import (
    _result_from,
    electron_record,
    get_result_object_from_storage,
    sublattice_dispatch_id,
)


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def get_mock_result(dispatch_id) -> SDKResult:
    """Construct a mock result object corresponding to a lattice."""

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        res1 = task(x)
        return res1

    workflow.build_graph(x=1)
    received_workflow = SDKLattice.deserialize_from_json(workflow.serialize_to_json())
    result_object = SDKResult(received_workflow, dispatch_id)

    return result_object


def test_result_from(mocker, test_db):
    """Test the result from function in the load module."""

    dispatch_id = "test_result_from"
    res = get_mock_result(dispatch_id)
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        mock_lattice_record = session.scalars(
            select(models.Lattice).where(models.Lattice.dispatch_id == dispatch_id)
        ).first()

        result_object = _result_from(mock_lattice_record)

        assert result_object._root_dispatch_id == mock_lattice_record.root_dispatch_id
        assert result_object._status == Status(mock_lattice_record.status)
        assert result_object._error == ""
        assert result_object.inputs == res.inputs
        assert result_object._start_time == mock_lattice_record.started_at
        assert result_object._end_time == mock_lattice_record.completed_at
        assert result_object.result == res.result


def test_get_result_object_from_storage(mocker):
    """Test the get_result_object_from_storage method."""
    from covalent_dispatcher._db.load import Lattice

    result_from_mock = mocker.patch("covalent_dispatcher._db.load._result_from")

    workflow_db_mock = mocker.patch("covalent_dispatcher._db.load.workflow_db")
    session_mock = workflow_db_mock.session.return_value.__enter__.return_value

    result_object = get_result_object_from_storage("mock-dispatch-id")

    assert call(Lattice) in session_mock.query.mock_calls
    session_mock.query().where().first.assert_called_once()

    assert result_object == result_from_mock.return_value
    result_from_mock.assert_called_once_with(session_mock.query().where().first.return_value)


def test_get_result_object_from_storage_exception(mocker):
    """Test the get_result_object_from_storage method."""
    from covalent_dispatcher._db.load import Lattice

    result_from_mock = mocker.patch("covalent_dispatcher._db.load._result_from")

    workflow_db_mock = mocker.patch("covalent_dispatcher._db.load.workflow_db")
    session_mock = workflow_db_mock.session.return_value.__enter__.return_value
    session_mock.query().where().first.return_value = None

    with pytest.raises(RuntimeError):
        get_result_object_from_storage("mock-dispatch-id")

    assert call(Lattice) in session_mock.query.mock_calls
    session_mock.query().where().first.assert_called_once()

    result_from_mock.assert_not_called()


def test_electron_record(mocker):
    """Test the electron_record method."""

    workflow_db_mock = mocker.patch("covalent_dispatcher._db.load.workflow_db")
    session_mock = workflow_db_mock.session.return_value.__enter__.return_value

    electron_record("mock-dispatch-id", "mock-node-id")
    session_mock.query().filter().filter().filter().first.assert_called_once()


def test_sublattice_dispatch_id(mocker):
    """Test the sublattice_dispatch_id method."""

    class MockObject:
        dispatch_id = "mock-dispatch-id"

    workflow_db_mock = mocker.patch("covalent_dispatcher._db.load.workflow_db")
    session_mock = workflow_db_mock.session.return_value.__enter__.return_value

    session_mock.query().filter().first.return_value = MockObject()
    res = sublattice_dispatch_id("mock-electron-id")
    assert res == "mock-dispatch-id"

    session_mock.query().filter().first.return_value = []
    res = sublattice_dispatch_id("mock-electron-id")
    assert res is None
