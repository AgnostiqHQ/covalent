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

"""Unit tests for the FastAPI asset endpoints"""

from contextlib import contextmanager
from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from covalent_dispatcher._service.assets import get_cached_result_object
from covalent_ui.app import fastapi_app as fast_app

DISPATCH_ID = "f34671d1-48f2-41ce-89d9-9a8cb5c60e5d"

INTERNAL_URI = "file:///tmp/object.pkl"

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
def mock_result_object():
    res_obj = MagicMock()
    mock_node = MagicMock()
    mock_asset = MagicMock()
    mock_asset.object_store = MagicMock()
    mock_asset.object_store.get_public_uri.return_value = "http://localhost:48008/files/output"

    res_obj.get_asset = MagicMock(return_value=mock_asset)
    res_obj.update_assets = MagicMock()
    res_obj.lattice.get_asset = MagicMock(return_value=mock_asset)
    res_obj.lattice.update_assets = MagicMock()

    res_obj.lattice.transport_graph.get_node = MagicMock(return_value=mock_node)

    mock_node.get_asset = MagicMock(return_value=mock_asset)
    mock_node.update_assets = MagicMock()

    return res_obj


def test_get_node_asset(mocker, client, test_db, mock_result_object):
    """
    Test get node asset
    """

    key = "output"
    node_id = 0
    dispatch_id = "test_get_node_asset_id"
    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    resp = client.get(f"/api/v2/dispatches/{dispatch_id}/electrons/{node_id}/assets/{key}")

    assert resp.json()["remote_uri"] == "http://localhost:48008/files/output"


def test_get_node_asset_bad_dispatch_id(mocker, client):
    """
    Test get node asset
    """
    key = "output"
    node_id = 0
    dispatch_id = "test_get_node_asset"
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    mocker.patch(
        "covalent_dispatcher._service.assets.get_cached_result_object",
        side_effect=HTTPException(status_code=400),
    )
    resp = client.get(f"/api/v2/dispatches/{dispatch_id}/electrons/{node_id}/assets/{key}")
    assert resp.status_code == 400


def test_post_node_asset(test_db, mocker, client, mock_result_object):
    """
    Test post node asset
    """

    key = "function"
    node_id = 0
    dispatch_id = "test_post_node_asset"

    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )

    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    resp = client.post(f"/api/v2/dispatches/{dispatch_id}/electrons/{node_id}/assets/{key}")
    assert resp.json()["remote_uri"] == "http://localhost:48008/files/output"


def test_post_node_asset_bad_dispatch_id(mocker, client):
    """
    Test post node asset
    """
    key = "function"
    node_id = 0
    dispatch_id = "test_put_node_asset_no_dispatch_id"

    mocker.patch(
        "covalent_dispatcher._service.assets.get_cached_result_object",
        side_effect=HTTPException(status_code=400),
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    resp = client.post(f"/api/v2/dispatches/{dispatch_id}/electrons/{node_id}/assets/{key}")
    assert resp.status_code == 400


def test_get_cached_result_obj(mocker, test_db):
    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._service.assets.get_result_object", side_effect=KeyError())
    with pytest.raises(HTTPException):
        get_cached_result_object("test_get_cached_result_obj")
