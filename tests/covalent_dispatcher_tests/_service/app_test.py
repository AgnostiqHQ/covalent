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


def test_submit(mocker, app, client):
    mocker.patch("covalent_dispatcher.run_dispatcher", return_value=DISPATCH_ID)
    response = client.post("/api/submit", data=json.dumps({}))
    assert response.json() == DISPATCH_ID

def test_cancel(mocker, test_db, client):
    """Test cancel workflow endpoint."""

    lattice_record = {"dispatch_id": DISPATCH_ID, "status": "RUNNING"}
    with test_db.session() as session:
        session.add(MockLattice(**lattice_record))
        session.commit()
    mock_cancel = mocker.patch(
        "covalent_dispatcher.cancel_running_dispatch",
        return_value=f"Dispatch {DISPATCH_ID} cancelled.",
        )

    response = client.post("/api/cancel", data=DISPATCH_ID.encode("utf-8"))
    assert response.json() == mock_cancel.return_value
    assert response.status_code == 200


def test_db_path(mocker, app, client):
    dbpath = "/Users/root/covalent/results.db"

    def __init__(self, dbpath=dbpath):
        self._dbpath = dbpath

    mocker.patch.object(DispatchDB, "__init__", __init__)
    response = client.get("/api/db-path")
    result = response.json().replace("\\", "").replace('"', "")
    assert result == dbpath


def test_get_result(mocker, app, client, test_db_file, tmp_path):
    lattice = MockLattice(
        status=str(Result.COMPLETED),
        dispatch_id=DISPATCH_ID,
    )

    with test_db_file.session() as session:
        session.add(lattice)
        session.commit()

    mocker.patch("covalent_dispatcher._service.app.result_from", return_value={})
    mocker.patch("covalent_dispatcher._service.app.workflow_db", test_db_file)
    mocker.patch("covalent_dispatcher._service.app.Lattice", MockLattice)
    response = client.get(f"/api/result/{DISPATCH_ID}")
    result = response.json()
    assert result["id"] == DISPATCH_ID
    assert result["status"] == str(Result.COMPLETED)
    os.remove("/tmp/testdb.sqlite")


def test_get_result_503(mocker, app, client, test_db_file, tmp_path):
    lattice = MockLattice(
        status=str(Result.NEW_OBJ),
        dispatch_id=DISPATCH_ID,
    )
    with test_db_file.session() as session:
        session.add(lattice)
        session.commit()
    mocker.patch("covalent_dispatcher._service.app.result_from", side_effect=FileNotFoundError())
    mocker.patch("covalent_dispatcher._service.app.workflow_db", test_db_file)
    mocker.patch("covalent_dispatcher._service.app.Lattice", MockLattice)
    response = client.get(f"/api/result/{DISPATCH_ID}?wait=True&status_only=True")
    assert response.status_code == 503
    os.remove("/tmp/testdb.sqlite")


def test_get_result_dispatch_id_not_found(mocker, test_db_file, client, tmp_path):

    mocker.patch.object(DispatchDB, "_get_data_store", test_db_file)
    mocker.patch("covalent_dispatcher._service.app.result_from", return_value={})
    mocker.patch("covalent_dispatcher._service.app.workflow_db", test_db_file)
    mocker.patch("covalent_dispatcher._service.app.Lattice", MockLattice)
    response = client.get(f"/api/result/{DISPATCH_ID}")
    assert response.status_code == 404


def test_db_path_get_config(mocker):
    dbpath = "/Users/root/covalent/results.db"

    get_config_mock = mocker.patch("covalent_dispatcher._db.dispatchdb.get_config")

    dispatch_db = DispatchDB()

    get_config_mock.assert_called_once()
