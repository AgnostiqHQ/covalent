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

"""Unit tests for the FastAPI app."""

import json
import tempfile
from contextlib import contextmanager
from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

import covalent as ct
from covalent._dispatcher_plugins.local import LocalDispatcher
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent_dispatcher._db.dispatchdb import DispatchDB
from covalent_dispatcher._service.app import _try_get_result_object, cancel_all_with_status
from covalent_ui.app import fastapi_app as fast_app

DISPATCH_ID = "f34671d1-48f2-41ce-89d9-9a8cb5c60e5d"

# Mock SqlAlchemy models
MockBase = declarative_base()


class MockLattice(MockBase):
    __tablename__ = "lattices"
    id = Column(Integer, primary_key=True)
    dispatch_id = Column(String(64), nullable=False)
    status = Column(String(24), nullable=False)


class MockDataStore:
    def __init__(self, db_URL):
        self.db_URL = db_URL
        self.engine = create_engine(self.db_URL)
        self.Session = sessionmaker(self.engine)

        MockBase.metadata.create_all(self.engine)

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        with self.Session.begin() as session:
            yield session


@pytest.fixture
def app():
    yield fast_app


@pytest.fixture
def client():
    with TestClient(fast_app) as c:
        yield c


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""
    return MockDataStore(db_URL="sqlite+pysqlite:///:memory:")


@pytest.fixture
def mock_manifest():
    """Create a mock workflow manifest"""

    @ct.electron
    def task(x):
        return x**2

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph(3)

    with tempfile.TemporaryDirectory() as staging_dir:
        manifest = LocalDispatcher.prepare_manifest(workflow, staging_dir)
    return manifest


@pytest.fixture
def test_db_file():
    """Instantiate and return a database."""
    return MockDataStore(db_URL="sqlite+pysqlite:////tmp/testdb.sqlite")


def test_cancel_dispatch(mocker, app, client):
    """
    Test cancelling dispatch
    """
    mocker.patch("covalent_dispatcher.entry_point.cancel_running_dispatch")
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    response = client.put(
        f"/api/v2/dispatches/{DISPATCH_ID}/status",
        json={"status": "CANCELLED"},
    )
    assert response.json() == f"Dispatch {DISPATCH_ID} cancelled."


def test_cancel_tasks(mocker, app, client):
    """
    Test cancelling tasks within a lattice after dispatch
    """
    mocker.patch("covalent_dispatcher.entry_point.cancel_running_dispatch")
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    response = client.put(
        f"/api/v2/dispatches/{DISPATCH_ID}/status",
        json={"status": "CANCELLED", "task_ids": [0, 1]},
    )
    assert response.json() == f"Cancelled tasks [0, 1] in dispatch {DISPATCH_ID}."


@pytest.mark.asyncio
async def test_cancel_exception(mocker, client):
    """Test the cancel endpoint."""
    cancel_running_dispatch_mock = mocker.patch(
        "covalent_dispatcher.entry_point.cancel_running_dispatch", side_effect=Exception("mock")
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    with pytest.raises(Exception):
        response = client.put(
            f"/api/v2/dispatches/{DISPATCH_ID}/status",
            json={"status": "CANCELLED", "task_ids": []},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Failed to cancel workflow: mock"
        cancel_running_dispatch_mock.assert_called_once_with(DISPATCH_ID, [])


def test_db_path_get_config(mocker):
    """Test that the db path is retrieved from the config.""" ""
    get_config_mock = mocker.patch("covalent_dispatcher._db.dispatchdb.get_config")

    DispatchDB()

    get_config_mock.assert_called_once()


def test_register(mocker, app, client, mock_manifest):
    mock_register_dispatch = mocker.patch(
        "covalent_dispatcher._service.app.dispatcher.register_dispatch", return_value=mock_manifest
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    resp = client.post("/api/v2/dispatches", data=mock_manifest.json())

    assert resp.json() == json.loads(mock_manifest.json())
    mock_register_dispatch.assert_awaited_with(mock_manifest, None)


def test_register_exception(mocker, app, client, mock_manifest):
    mock_register_dispatch = mocker.patch(
        "covalent_dispatcher._service.app.dispatcher.register_dispatch", side_effect=RuntimeError()
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    resp = client.post("/api/v2/dispatches", data=mock_manifest.json())
    assert resp.status_code == 400


def test_register_sublattice(mocker, app, client, mock_manifest):
    mock_register_dispatch = mocker.patch(
        "covalent_dispatcher._service.app.dispatcher.register_dispatch", return_value=mock_manifest
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    resp = client.post(
        "/api/v2/dispatches/parent_dispatch/sublattices",
        data=mock_manifest.json(),
    )

    assert resp.json() == json.loads(mock_manifest.json())
    mock_register_dispatch.assert_awaited_with(mock_manifest, "parent_dispatch")


def test_register_redispatch(mocker, app, client, mock_manifest):
    dispatch_id = "test_register_redispatch"
    mock_register_redispatch = mocker.patch(
        "covalent_dispatcher._service.app.dispatcher.register_redispatch",
        return_value=mock_manifest,
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    resp = client.post(f"/api/v2/dispatches/{dispatch_id}/redispatches", data=mock_manifest.json())
    mock_register_redispatch.assert_awaited_with(mock_manifest, dispatch_id, False)
    assert resp.json() == json.loads(mock_manifest.json())


def test_register_redispatch_reuse(mocker, app, client, mock_manifest):
    dispatch_id = "test_register_redispatch"
    mock_register_redispatch = mocker.patch(
        "covalent_dispatcher._service.app.dispatcher.register_redispatch",
        return_value=mock_manifest,
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    resp = client.post(
        f"/api/v2/dispatches/{dispatch_id}/redispatches",
        data=mock_manifest.json(),
        params={"reuse_previous_results": True},
    )
    mock_register_redispatch.assert_awaited_with(mock_manifest, dispatch_id, True)
    assert resp.json() == json.loads(mock_manifest.json())


def test_register_redispatch_exception(mocker, app, client, mock_manifest):
    dispatch_id = "test_register_redispatch"
    mock_register_redispatch = mocker.patch(
        "covalent_dispatcher._service.app.dispatcher.register_redispatch",
        side_effect=RuntimeError(),
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    resp = client.post(f"/api/v2/dispatches/{dispatch_id}/redispatches", data=mock_manifest.json())
    assert resp.status_code == 400


def test_start(mocker, app, client):
    dispatch_id = "test_start"
    mock_start = mocker.patch("covalent_dispatcher._service.app.dispatcher.start_dispatch")
    mock_create_task = mocker.patch("asyncio.create_task")
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    resp = client.put(f"/api/v2/dispatches/{dispatch_id}/status", json={"status": "RUNNING"})
    assert resp.json() == dispatch_id


def test_export_manifest(mocker, app, client, mock_manifest):
    dispatch_id = "test_export_manifest"
    mock_result_object = MagicMock()
    mock_result_object.get_value = MagicMock(return_value=str(RESULT_STATUS.NEW_OBJECT))
    mocker.patch(
        "covalent_dispatcher._service.app._try_get_result_object", return_value=mock_result_object
    )
    mock_export = mocker.patch(
        "covalent_dispatcher._service.app.export_result_manifest", return_value=mock_manifest
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    resp = client.get(f"/api/v2/dispatches/{dispatch_id}")
    assert resp.json() == json.loads(mock_manifest.json())


def test_export_manifest_bad_dispatch_id(mocker, app, client, mock_manifest):
    dispatch_id = "test_export_manifest"
    mock_result_object = MagicMock()
    mock_result_object.get_value = MagicMock(return_value=str(RESULT_STATUS.NEW_OBJECT))
    mocker.patch("covalent_dispatcher._service.app._try_get_result_object", return_value=None)
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    resp = client.get(f"/api/v2/dispatches/{dispatch_id}")
    assert resp.status_code == 404


def test_try_get_result_object(mocker, app, client, mock_manifest):
    dispatch_id = "test_try_get_result_object"
    mock_result_object = MagicMock()
    mocker.patch(
        "covalent_dispatcher._service.app.get_result_object", return_value=mock_result_object
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    assert _try_get_result_object(dispatch_id) == mock_result_object


def test_try_get_result_object_not_found(mocker, app, client, mock_manifest):
    dispatch_id = "test_try_get_result_object"
    mock_result_object = MagicMock()
    mocker.patch("covalent_dispatcher._service.app.get_result_object", side_effect=KeyError())
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    assert _try_get_result_object(dispatch_id) is None


@pytest.mark.asyncio
async def test_cancel_all_with_status(mocker, test_db):
    mock_rec = MagicMock()
    mock_rec.dispatch_id = "mock_dispatch"

    mocker.patch("covalent_dispatcher._service.app.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.Result.get_db_records", return_value=[mock_rec])
    mock_cancel = mocker.patch(
        "covalent_dispatcher._service.app.dispatcher.cancel_running_dispatch"
    )

    await cancel_all_with_status(RESULT_STATUS.RUNNING)

    mock_cancel.assert_awaited_with("mock_dispatch")
