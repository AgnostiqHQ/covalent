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

"""Unit tests for the Flask app."""

import json
from datetime import datetime

import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from covalent._data_store import models
from covalent._data_store.models import Lattice
from covalent._results_manager.result import Result
from covalent_dispatcher._db.dispatchdb import DispatchDB
from covalent_dispatcher._service.app import bp as dispatcher

DISPATCH_ID = "f34671d1-48f2-41ce-89d9-9a8cb5c60e5d"

flask_app = Flask(__name__)
flask_app.register_blueprint(dispatcher)


@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


class MockDataStore:
    def __init__(self, lattice, dbpath):
        engine = create_engine("sqlite+pysqlite:///" + str(dbpath / "workflow_db.sqlite"))
        models.Base.metadata.create_all(engine)
        session = Session(engine)
        if lattice:
            session.add(lattice)
        session.commit()
        self.engine = engine


def test_submit(mocker, app, client):
    mocker.patch("covalent_dispatcher.run_dispatcher", return_value=DISPATCH_ID)
    response = client.post("/api/submit", data=json.dumps({}))
    assert json.loads(response.data) == DISPATCH_ID


def test_cancel(app, client):
    response = client.post("/api/cancel", data=DISPATCH_ID.encode("utf-8"))
    assert json.loads(response.data) == f"Dispatch {DISPATCH_ID} cancelled."


def test_db_path(mocker, app, client):
    dbpath = "/Users/root/covalent/results.db"

    def __init__(self, dbpath=dbpath):
        self._dbpath = dbpath

    mocker.patch.object(DispatchDB, "__init__", __init__)
    response = client.get("/api/db-path")
    assert json.loads(response.data) == dbpath


def test_get_result(mocker, app, client, tmp_path):
    lattice = Lattice(
        status=str(Result.COMPLETED),
        dispatch_id=DISPATCH_ID,
        name="test-lattice",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=False,
        electron_num=0,
        completed_electron_num=0,
    )

    def _get_data_store(self, initialize_db=False):
        return MockDataStore(lattice, tmp_path)

    mocker.patch.object(DispatchDB, "_get_data_store", _get_data_store)
    mocker.patch("covalent_dispatcher._service.app.result_from", return_value={})
    response = client.get(f"/api/result/{DISPATCH_ID}")
    result = json.loads(response.data)
    assert result["id"] == DISPATCH_ID
    assert result["status"] == str(Result.COMPLETED)


def test_get_result_503(mocker, app, client, tmp_path):
    lattice = Lattice(
        status=str(Result.NEW_OBJ),
        dispatch_id=DISPATCH_ID,
        name="test-lattice",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=False,
        electron_num=0,
        completed_electron_num=0,
    )

    def _get_data_store(self, initialize_db=False):
        return MockDataStore(lattice, tmp_path)

    mocker.patch.object(DispatchDB, "_get_data_store", _get_data_store)
    mocker.patch("covalent_dispatcher._service.app.result_from", return_value={})
    response = client.get(
        f"/api/result/{DISPATCH_ID}", query_string={"wait": True, "status_only": True}
    )
    assert response.status_code == 503


def test_get_result_dispatch_id_not_found(mocker, app, client, tmp_path):
    def _get_data_store(self, initialize_db=False):
        return MockDataStore(None, tmp_path)

    mocker.patch.object(DispatchDB, "_get_data_store", _get_data_store)
    mocker.patch("covalent_dispatcher._service.app.result_from", return_value={})
    response = client.get(f"/api/result/{DISPATCH_ID}")
    assert response.status_code == 404
