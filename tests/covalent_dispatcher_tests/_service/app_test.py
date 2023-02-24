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
import os
from contextlib import contextmanager
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from covalent._results_manager.result import Result
from covalent_dispatcher._db.dispatchdb import DispatchDB
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
def test_db_file():
    """Instantiate and return a database."""
    return MockDataStore(db_URL="sqlite+pysqlite:////tmp/testdb.sqlite")


@pytest.mark.asyncio
@pytest.mark.parametrize("disable_run", [True, False])
async def test_submit(mocker, client, disable_run):
    """Test the submit endpoint."""
    mock_data = json.dumps({}).encode("utf-8")
    run_dispatcher_mock = mocker.patch(
        "covalent_dispatcher.run_dispatcher", return_value=DISPATCH_ID
    )
    response = client.post("/api/submit", data=mock_data, params={"disable_run": disable_run})
    assert response.json() == DISPATCH_ID
    run_dispatcher_mock.assert_called_once_with(mock_data, disable_run)


@pytest.mark.asyncio
async def test_submit_exception(mocker, client):
    """Test the submit endpoint."""
    mock_data = json.dumps({}).encode("utf-8")
    mocker.patch("covalent_dispatcher.run_dispatcher", side_effect=Exception("mock"))
    response = client.post("/api/submit", data=mock_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Failed to submit workflow: mock"


@pytest.mark.asyncio
@pytest.mark.parametrize("is_pending", [True, False])
async def test_redispatch(mocker, client, is_pending):
    """Test the redispatch endpoint."""
    json_lattice = None
    electron_updates = None
    reuse_previous_results = False
    mock_data = json.dumps(
        {
            "dispatch_id": DISPATCH_ID,
            "json_lattice": json_lattice,
            "electron_updates": electron_updates,
            "reuse_previous_results": reuse_previous_results,
        }
    ).encode("utf-8")
    run_redispatch_mock = mocker.patch(
        "covalent_dispatcher.run_redispatch", return_value=DISPATCH_ID
    )

    response = client.post("/api/redispatch", data=mock_data, params={"is_pending": is_pending})
    assert response.json() == DISPATCH_ID
    run_redispatch_mock.assert_called_once_with(
        DISPATCH_ID, json_lattice, electron_updates, reuse_previous_results, is_pending
    )


def test_cancel_dispatch(mocker, app, client):
    """
    Test cancelling dispatch
    """
    mocker.patch("covalent_dispatcher.cancel_running_dispatch")
    response = client.post(
        "/api/cancel", data=json.dumps({"dispatch_id": DISPATCH_ID, "task_ids": []})
    )
    assert response.json() == f"Dispatch {DISPATCH_ID} cancelled."


def test_cancel_tasks(mocker, app, client):
    """
    Test cancelling tasks within a lattice after dispatch
    """
    mocker.patch("covalent_dispatcher.cancel_running_dispatch")
    response = client.post(
        "/api/cancel", data=json.dumps({"dispatch_id": DISPATCH_ID, "task_ids": [0, 1]})
    )
    assert response.json() == f"Cancelled tasks [0, 1] in dispatch {DISPATCH_ID}."


@pytest.mark.asyncio
async def test_redispatch_exception(mocker, client):
    """Test the redispatch endpoint."""
    response = client.post("/api/redispatch", data="bad data")
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Failed to redispatch workflow: Expecting value: line 1 column 1 (char 0)"
    )


@pytest.mark.asyncio
async def test_cancel(mocker, client):
    """Test the cancel endpoint."""
    cancel_running_dispatch_mock = mocker.patch(
        "covalent_dispatcher.cancel_running_dispatch", return_value=DISPATCH_ID
    )
    response = client.post(
        "/api/cancel", data=json.dumps({"dispatch_id": DISPATCH_ID, "task_ids": []})
    )
    assert response.json() == f"Dispatch {DISPATCH_ID} cancelled."
    cancel_running_dispatch_mock.assert_called_once_with(DISPATCH_ID, [])


@pytest.mark.asyncio
async def test_cancel_exception(mocker, client):
    """Test the cancel endpoint."""
    cancel_running_dispatch_mock = mocker.patch(
        "covalent_dispatcher.cancel_running_dispatch", side_effect=Exception("mock")
    )

    with pytest.raises(Exception):
        response = client.post(
            "/api/cancel", data=json.dumps({"dispatch_id": DISPATCH_ID, "task_ids": []})
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Failed to cancel workflow: mock"
        cancel_running_dispatch_mock.assert_called_once_with(DISPATCH_ID, [])


def test_get_result(mocker, client, test_db_file):
    """Test the get-result endpoint."""
    lattice = MockLattice(
        status=str(Result.COMPLETED),
        dispatch_id=DISPATCH_ID,
    )

    with test_db_file.session() as session:
        session.add(lattice)
        session.commit()

    mocker.patch("covalent_dispatcher._service.app._result_from", return_value={})
    mocker.patch("covalent_dispatcher._service.app.workflow_db", test_db_file)
    mocker.patch("covalent_dispatcher._service.app.Lattice", MockLattice)
    response = client.get(f"/api/result/{DISPATCH_ID}")
    result = response.json()
    assert result["id"] == DISPATCH_ID
    assert result["status"] == str(Result.COMPLETED)
    os.remove("/tmp/testdb.sqlite")


def test_get_result_503(mocker, client, test_db_file):
    """Test the get-result endpoint."""
    lattice = MockLattice(
        status=str(Result.NEW_OBJ),
        dispatch_id=DISPATCH_ID,
    )
    with test_db_file.session() as session:
        session.add(lattice)
        session.commit()
    mocker.patch("covalent_dispatcher._service.app._result_from", side_effect=FileNotFoundError())
    mocker.patch("covalent_dispatcher._service.app.workflow_db", test_db_file)
    mocker.patch("covalent_dispatcher._service.app.Lattice", MockLattice)
    response = client.get(f"/api/result/{DISPATCH_ID}?wait=True&status_only=True")
    assert response.status_code == 503
    os.remove("/tmp/testdb.sqlite")


def test_get_result_dispatch_id_not_found(mocker, test_db_file, client):
    """Test the get-result endpoint and that 404 is returned if the dispatch ID is not found in the database."""
    mocker.patch("covalent_dispatcher._service.app._result_from", return_value={})
    mocker.patch("covalent_dispatcher._service.app.workflow_db", test_db_file)
    mocker.patch("covalent_dispatcher._service.app.Lattice", MockLattice)
    response = client.get(f"/api/result/{DISPATCH_ID}")
    assert response.status_code == 404


def test_db_path_get_config(mocker):
    """Test that the db path is retrieved from the config.""" ""
    get_config_mock = mocker.patch("covalent_dispatcher._db.dispatchdb.get_config")

    DispatchDB()

    get_config_mock.assert_called_once()
