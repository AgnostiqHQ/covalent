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
from covalent_dispatcher._service.app import _try_get_result_object
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


@pytest.mark.asyncio
async def test_submit(mocker, client):
    """Test the submit endpoint."""
    mock_data = json.dumps({}).encode("utf-8")
    run_dispatcher_mock = mocker.patch(
        "covalent_dispatcher.entry_point.make_dispatch", return_value=DISPATCH_ID
    )
    response = client.post("/api/v1/dispatch/submit", data=mock_data)
    assert response.json() == DISPATCH_ID
    run_dispatcher_mock.assert_called_once_with(mock_data)


@pytest.mark.asyncio
async def test_submit_exception(mocker, client):
    """Test the submit endpoint."""
    mock_data = json.dumps({}).encode("utf-8")
    mocker.patch("covalent_dispatcher.entry_point.make_dispatch", side_effect=Exception("mock"))
    response = client.post("/api/v1/dispatch/submit", data=mock_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Failed to submit workflow: mock"


def test_cancel_dispatch(mocker, app, client):
    """
    Test cancelling dispatch
    """
    mocker.patch("covalent_dispatcher.entry_point.cancel_running_dispatch")
    response = client.post(
        "/api/v1/dispatch/cancel", data=json.dumps({"dispatch_id": DISPATCH_ID, "task_ids": []})
    )
    assert response.json() == f"Dispatch {DISPATCH_ID} cancelled."


def test_cancel_tasks(mocker, app, client):
    """
    Test cancelling tasks within a lattice after dispatch
    """
    mocker.patch("covalent_dispatcher.entry_point.cancel_running_dispatch")
    response = client.post(
        "/api/v1/dispatch/cancel",
        data=json.dumps({"dispatch_id": DISPATCH_ID, "task_ids": [0, 1]}),
    )
    assert response.json() == f"Cancelled tasks [0, 1] in dispatch {DISPATCH_ID}."


@pytest.mark.asyncio
async def test_cancel(mocker, client):
    """Test the cancel endpoint."""
    cancel_running_dispatch_mock = mocker.patch(
        "covalent_dispatcher.entry_point.cancel_running_dispatch", return_value=DISPATCH_ID
    )
    response = client.post(
        "/api/v1/dispatch/cancel", data=json.dumps({"dispatch_id": DISPATCH_ID, "task_ids": []})
    )
    assert response.json() == f"Dispatch {DISPATCH_ID} cancelled."
    cancel_running_dispatch_mock.assert_called_once_with(DISPATCH_ID, [])


@pytest.mark.asyncio
async def test_cancel_exception(mocker, client):
    """Test the cancel endpoint."""
    cancel_running_dispatch_mock = mocker.patch(
        "covalent_dispatcher.entry_point.cancel_running_dispatch", side_effect=Exception("mock")
    )

    with pytest.raises(Exception):
        response = client.post(
            "/api/v1/dispatch/cancel",
            data=json.dumps({"dispatch_id": DISPATCH_ID, "task_ids": []}),
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
    resp = client.post("/api/v1/dispatch/register", data=mock_manifest.json())

    assert resp.json() == json.loads(mock_manifest.json())
    mock_register_dispatch.assert_awaited_with(mock_manifest, None)


def test_register_exception(mocker, app, client, mock_manifest):
    mock_register_dispatch = mocker.patch(
        "covalent_dispatcher._service.app.dispatcher.register_dispatch", side_effect=RuntimeError()
    )
    resp = client.post("/api/v1/dispatch/register", data=mock_manifest.json())
    assert resp.status_code == 400


def test_register_sublattice(mocker, app, client, mock_manifest):
    mock_register_dispatch = mocker.patch(
        "covalent_dispatcher._service.app.dispatcher.register_dispatch", return_value=mock_manifest
    )
    resp = client.post(
        "/api/v1/dispatch/register",
        data=mock_manifest.json(),
        params={"parent_dispatch_id": "parent_dispatch"},
    )

    assert resp.json() == json.loads(mock_manifest.json())
    mock_register_dispatch.assert_awaited_with(mock_manifest, "parent_dispatch")


def test_register_redispatch(mocker, app, client, mock_manifest):
    dispatch_id = "test_register_redispatch"
    mock_register_redispatch = mocker.patch(
        "covalent_dispatcher._service.app.dispatcher.register_redispatch",
        return_value=mock_manifest,
    )
    resp = client.post(f"/api/v1/dispatch/register/{dispatch_id}", data=mock_manifest.json())
    mock_register_redispatch.assert_awaited_with(mock_manifest, dispatch_id, False)
    assert resp.json() == json.loads(mock_manifest.json())


def test_register_redispatch_reuse(mocker, app, client, mock_manifest):
    dispatch_id = "test_register_redispatch"
    mock_register_redispatch = mocker.patch(
        "covalent_dispatcher._service.app.dispatcher.register_redispatch",
        return_value=mock_manifest,
    )
    resp = client.post(
        f"/api/v1/dispatch/register/{dispatch_id}",
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
    resp = client.post(f"/api/v1/dispatch/register/{dispatch_id}", data=mock_manifest.json())
    assert resp.status_code == 400


def test_start(mocker, app, client):
    dispatch_id = "test_start"
    mock_start = mocker.patch("covalent_dispatcher._service.app.dispatcher.start_dispatch")
    mock_create_task = mocker.patch("asyncio.create_task")
    resp = client.put(f"/api/v1/dispatch/start/{dispatch_id}")
    assert resp.json() == dispatch_id


def test_export_result_nowait(mocker, app, client, mock_manifest):
    dispatch_id = "test_export_result"
    mock_result_object = MagicMock()
    mock_result_object.get_value = MagicMock(return_value=str(RESULT_STATUS.NEW_OBJECT))
    mocker.patch(
        "covalent_dispatcher._service.app._try_get_result_object", return_value=mock_result_object
    )
    mock_export = mocker.patch(
        "covalent_dispatcher._service.app.export_result_manifest", return_value=mock_manifest
    )
    resp = client.get(f"/api/v1/dispatch/export/{dispatch_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == dispatch_id
    assert resp.json()["status"] == str(RESULT_STATUS.NEW_OBJECT)
    assert resp.json()["result_export"] == json.loads(mock_manifest.json())


def test_export_result_wait_not_ready(mocker, app, client, mock_manifest):
    dispatch_id = "test_export_result"
    mock_result_object = MagicMock()
    mock_result_object.get_value = MagicMock(return_value=str(RESULT_STATUS.RUNNING))
    mocker.patch(
        "covalent_dispatcher._service.app._try_get_result_object", return_value=mock_result_object
    )
    mock_export = mocker.patch(
        "covalent_dispatcher._service.app.export_result_manifest", return_value=mock_manifest
    )
    resp = client.get(f"/api/v1/dispatch/export/{dispatch_id}", params={"wait": True})
    assert resp.status_code == 503


def test_export_result_bad_dispatch_id(mocker, app, client, mock_manifest):
    dispatch_id = "test_export_result"
    mock_result_object = MagicMock()
    mock_result_object.get_value = MagicMock(return_value=str(RESULT_STATUS.NEW_OBJECT))
    mocker.patch("covalent_dispatcher._service.app._try_get_result_object", return_value=None)
    resp = client.get(f"/api/v1/dispatch/export/{dispatch_id}")
    assert resp.status_code == 404


def test_try_get_result_object(mocker, app, client, mock_manifest):
    dispatch_id = "test_try_get_result_object"
    mock_result_object = MagicMock()
    mocker.patch(
        "covalent_dispatcher._service.app.get_result_object", return_value=mock_result_object
    )
    assert _try_get_result_object(dispatch_id) == mock_result_object


def test_try_get_result_object_not_found(mocker, app, client, mock_manifest):
    dispatch_id = "test_try_get_result_object"
    mock_result_object = MagicMock()
    mocker.patch("covalent_dispatcher._service.app.get_result_object", side_effect=KeyError())
    assert _try_get_result_object(dispatch_id) is None
