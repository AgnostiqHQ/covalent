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

import base64
import tempfile
from contextlib import contextmanager
from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from covalent._workflow.transportable_object import TransportableObject
from covalent_dispatcher._service.assets import (
    _generate_file_slice,
    _get_tobj_pickle_offsets,
    _get_tobj_string_offsets,
    get_cached_result_object,
)
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
    mock_asset.internal_uri = INTERNAL_URI

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

    class MockGenerateFileSlice:
        def __init__(self):
            self.calls = []

        def __call__(self, file_url: str, start_byte: int, end_byte: int, chunk_size: int = 65536):
            self.calls.append((file_url, start_byte, end_byte, chunk_size))
            yield "Hi"

    key = "output"
    node_id = 0
    dispatch_id = "test_get_node_asset_no_dispatch_id"
    mock_generator = MockGenerateFileSlice()

    mocker.patch("fastapi.responses.StreamingResponse")
    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )
    mock_generate_file_slice = mocker.patch(
        "covalent_dispatcher._service.assets._generate_file_slice", mock_generator
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    resp = client.get(f"/api/v2/dispatches/{dispatch_id}/electrons/{node_id}/assets/{key}")

    assert resp.text == "Hi"
    assert (INTERNAL_URI, 0, -1, 65536) == mock_generator.calls[0]


def test_get_node_asset_byte_range(mocker, client, test_db, mock_result_object):
    """
    Test get node asset
    """

    test_str = "test_get_node_asset_string_rep"

    class MockGenerateFileSlice:
        def __init__(self):
            self.calls = []

        def __call__(self, file_url: str, start_byte: int, end_byte: int, chunk_size: int = 65536):
            self.calls.append((file_url, start_byte, end_byte, chunk_size))
            if end_byte >= 0:
                yield test_str[start_byte:end_byte]
            else:
                yield test_str[start_byte:]

    key = "output"
    node_id = 0
    dispatch_id = "test_get_node_asset_no_dispatch_id"
    mock_generator = MockGenerateFileSlice()

    mocker.patch("fastapi.responses.StreamingResponse")
    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )
    mock_generate_file_slice = mocker.patch(
        "covalent_dispatcher._service.assets._generate_file_slice", mock_generator
    )

    headers = {"Range": "bytes=0-6"}
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    resp = client.get(
        f"/api/v2/dispatches/{dispatch_id}/electrons/{node_id}/assets/{key}", headers=headers
    )

    assert resp.text == test_str[0:6]
    assert (INTERNAL_URI, 0, 6, 65536) == mock_generator.calls[0]


@pytest.mark.parametrize("rep,start_byte,end_byte", [("string", 0, 6), ("object", 6, 12)])
def test_get_node_asset_rep(
    mocker, client, test_db, mock_result_object, rep, start_byte, end_byte
):
    """
    Test get node asset
    """

    test_str = "test_get_node_asset_rep"

    class MockGenerateFileSlice:
        def __init__(self):
            self.calls = []

        def __call__(self, file_url: str, start_byte: int, end_byte: int, chunk_size: int = 65536):
            self.calls.append((file_url, start_byte, end_byte, chunk_size))
            if end_byte >= 0:
                yield test_str[start_byte:end_byte]
            else:
                yield test_str[start_byte:]

    key = "output"
    node_id = 0
    dispatch_id = "test_get_node_asset_no_dispatch_id"
    mock_generator = MockGenerateFileSlice()

    mocker.patch("fastapi.responses.StreamingResponse")
    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )
    mock_generate_file_slice = mocker.patch(
        "covalent_dispatcher._service.assets._generate_file_slice", mock_generator
    )
    mocker.patch(
        "covalent_dispatcher._service.assets._get_tobj_string_offsets", return_value=(0, 6)
    )
    mocker.patch(
        "covalent_dispatcher._service.assets._get_tobj_pickle_offsets", return_value=(6, 12)
    )

    params = {"representation": rep}
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    resp = client.get(
        f"/api/v2/dispatches/{dispatch_id}/electrons/{node_id}/assets/{key}", params=params
    )

    assert resp.text == test_str[start_byte:end_byte]
    assert (INTERNAL_URI, start_byte, end_byte, 65536) == mock_generator.calls[0]


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


def test_get_lattice_asset(mocker, client, test_db, mock_result_object):
    """
    Test get lattice asset
    """

    class MockGenerateFileSlice:
        def __init__(self):
            self.calls = []

        def __call__(self, file_url: str, start_byte: int, end_byte: int, chunk_size: int = 65536):
            self.calls.append((file_url, start_byte, end_byte, chunk_size))
            yield "Hi"

    key = "workflow_function"
    dispatch_id = "test_get_lattice_asset_no_dispatch_id"
    mock_generator = MockGenerateFileSlice()

    mocker.patch("fastapi.responses.StreamingResponse")
    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )
    mock_generate_file_slice = mocker.patch(
        "covalent_dispatcher._service.assets._generate_file_slice", mock_generator
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    resp = client.get(f"/api/v2/dispatches/{dispatch_id}/lattice/assets/{key}")

    assert resp.text == "Hi"
    assert (INTERNAL_URI, 0, -1, 65536) == mock_generator.calls[0]


def test_get_lattice_asset_byte_range(mocker, client, test_db, mock_result_object):
    """
    Test get lattice asset
    """

    test_str = "test_lattice_asset_byte_range"

    class MockGenerateFileSlice:
        def __init__(self):
            self.calls = []

        def __call__(self, file_url: str, start_byte: int, end_byte: int, chunk_size: int = 65536):
            self.calls.append((file_url, start_byte, end_byte, chunk_size))
            if end_byte >= 0:
                yield test_str[start_byte:end_byte]
            else:
                yield test_str[start_byte:]

    key = "workflow_function"
    dispatch_id = "test_get_lattice_asset_no_dispatch_id"
    mock_generator = MockGenerateFileSlice()

    mocker.patch("fastapi.responses.StreamingResponse")
    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )
    mock_generate_file_slice = mocker.patch(
        "covalent_dispatcher._service.assets._generate_file_slice", mock_generator
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    headers = {"Range": "bytes=0-6"}
    resp = client.get(f"/api/v2/dispatches/{dispatch_id}/lattice/assets/{key}", headers=headers)

    assert resp.text == test_str[0:6]
    assert (INTERNAL_URI, 0, 6, 65536) == mock_generator.calls[0]


@pytest.mark.parametrize("rep,start_byte,end_byte", [("string", 0, 6), ("object", 6, 12)])
def test_get_lattice_asset_rep(
    mocker, client, test_db, mock_result_object, rep, start_byte, end_byte
):
    """
    Test get lattice asset
    """

    test_str = "test_get_lattice_asset_rep"

    class MockGenerateFileSlice:
        def __init__(self):
            self.calls = []

        def __call__(self, file_url: str, start_byte: int, end_byte: int, chunk_size: int = 65536):
            self.calls.append((file_url, start_byte, end_byte, chunk_size))
            if end_byte >= 0:
                yield test_str[start_byte:end_byte]
            else:
                yield test_str[start_byte:]

    key = "workflow_function"
    dispatch_id = "test_get_lattice_asset_rep"
    mock_generator = MockGenerateFileSlice()

    mocker.patch("fastapi.responses.StreamingResponse")
    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )
    mock_generate_file_slice = mocker.patch(
        "covalent_dispatcher._service.assets._generate_file_slice", mock_generator
    )
    mocker.patch(
        "covalent_dispatcher._service.assets._get_tobj_string_offsets", return_value=(0, 6)
    )
    mocker.patch(
        "covalent_dispatcher._service.assets._get_tobj_pickle_offsets", return_value=(6, 12)
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    params = {"representation": rep}

    resp = client.get(f"/api/v2/dispatches/{dispatch_id}/lattice/assets/{key}", params=params)

    assert resp.text == test_str[start_byte:end_byte]
    assert (INTERNAL_URI, start_byte, end_byte, 65536) == mock_generator.calls[0]


def test_get_lattice_asset_bad_dispatch_id(mocker, client):
    """
    Test get lattice asset
    """

    key = "workflow_function"
    dispatch_id = "test_get_lattice_asset_no_dispatch_id"

    mocker.patch(
        "covalent_dispatcher._service.assets.get_cached_result_object",
        side_effect=HTTPException(status_code=400),
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    resp = client.get(f"/api/v2/dispatches/{dispatch_id}/lattice/assets/{key}")
    assert resp.status_code == 400


def test_get_dispatch_asset(mocker, client, test_db, mock_result_object):
    """
    Test get dispatch asset
    """

    class MockGenerateFileSlice:
        def __init__(self):
            self.calls = []

        def __call__(self, file_url: str, start_byte: int, end_byte: int, chunk_size: int = 65536):
            self.calls.append((file_url, start_byte, end_byte, chunk_size))
            yield "Hi"

    key = "result"
    dispatch_id = "test_get_dispatch_asset"
    mock_generator = MockGenerateFileSlice()

    mocker.patch("fastapi.responses.StreamingResponse")
    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )
    mock_generate_file_slice = mocker.patch(
        "covalent_dispatcher._service.assets._generate_file_slice", mock_generator
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    resp = client.get(f"/api/v2/dispatches/{dispatch_id}/assets/{key}")

    assert resp.text == "Hi"
    assert (INTERNAL_URI, 0, -1, 65536) == mock_generator.calls[0]


def test_get_dispatch_asset_byte_range(mocker, client, test_db, mock_result_object):
    """
    Test get dispatch asset
    """

    test_str = "test_dispatch_asset_byte_range"

    class MockGenerateFileSlice:
        def __init__(self):
            self.calls = []

        def __call__(self, file_url: str, start_byte: int, end_byte: int, chunk_size: int = 65536):
            self.calls.append((file_url, start_byte, end_byte, chunk_size))
            if end_byte >= 0:
                yield test_str[start_byte:end_byte]
            else:
                yield test_str[start_byte:]

    key = "result"
    dispatch_id = "test_get_dispatch_asset_byte_range"
    mock_generator = MockGenerateFileSlice()

    mocker.patch("fastapi.responses.StreamingResponse")
    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    mock_generate_file_slice = mocker.patch(
        "covalent_dispatcher._service.assets._generate_file_slice", mock_generator
    )

    headers = {"Range": "bytes=0-6"}
    resp = client.get(f"/api/v2/dispatches/{dispatch_id}/assets/{key}", headers=headers)

    assert resp.text == test_str[0:6]
    assert (INTERNAL_URI, 0, 6, 65536) == mock_generator.calls[0]


@pytest.mark.parametrize("rep,start_byte,end_byte", [("string", 0, 6), ("object", 6, 12)])
def test_get_dispatch_asset_rep(
    mocker, client, test_db, mock_result_object, rep, start_byte, end_byte
):
    """
    Test get dispatch asset
    """

    test_str = "test_get_dispatch_asset_rep"

    class MockGenerateFileSlice:
        def __init__(self):
            self.calls = []

        def __call__(self, file_url: str, start_byte: int, end_byte: int, chunk_size: int = 65536):
            self.calls.append((file_url, start_byte, end_byte, chunk_size))
            if end_byte >= 0:
                yield test_str[start_byte:end_byte]
            else:
                yield test_str[start_byte:]

    key = "result"
    dispatch_id = "test_get_dispatch_asset_rep"
    mock_generator = MockGenerateFileSlice()

    mocker.patch("fastapi.responses.StreamingResponse")
    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )
    mock_generate_file_slice = mocker.patch(
        "covalent_dispatcher._service.assets._generate_file_slice", mock_generator
    )
    mocker.patch(
        "covalent_dispatcher._service.assets._get_tobj_string_offsets", return_value=(0, 6)
    )
    mocker.patch(
        "covalent_dispatcher._service.assets._get_tobj_pickle_offsets", return_value=(6, 12)
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    params = {"representation": rep}

    resp = client.get(f"/api/v2/dispatches/{dispatch_id}/assets/{key}", params=params)

    assert resp.text == test_str[start_byte:end_byte]
    assert (INTERNAL_URI, start_byte, end_byte, 65536) == mock_generator.calls[0]


def test_get_dispatch_asset_bad_dispatch_id(mocker, client):
    """
    Test get dispatch asset
    """

    key = "result"
    dispatch_id = "test_get_dispatch_asset_no_dispatch_id"

    mocker.patch(
        "covalent_dispatcher._service.assets.get_cached_result_object",
        side_effect=HTTPException(status_code=400),
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    resp = client.get(f"/api/v2/dispatches/{dispatch_id}/assets/{key}")
    assert resp.status_code == 400


def test_put_node_asset(test_db, mocker, client, mock_result_object):
    """
    Test put node asset
    """

    key = "function"
    node_id = 0
    dispatch_id = "test_put_node_asset"

    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )

    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    with tempfile.NamedTemporaryFile("w") as writer:
        writer.write(f"{dispatch_id}")
        writer.flush()

        headers = {"Digest-alg": "sha", "Digest": "0bf"}
        with open(writer.name, "rb") as reader:
            resp = client.put(
                f"/api/v2/dispatches/{dispatch_id}/electrons/{node_id}/assets/{key}",
                data=reader,
                headers=headers,
            )
        mock_node = mock_result_object.lattice.transport_graph.get_node(node_id)
        mock_node.update_assets.assert_called()
        assert resp.status_code == 200


def test_put_node_asset_bad_dispatch_id(mocker, client):
    """
    Test put node asset
    """
    key = "function"
    node_id = 0
    dispatch_id = "test_put_node_asset_no_dispatch_id"

    mocker.patch(
        "covalent_dispatcher._service.assets.get_cached_result_object",
        side_effect=HTTPException(status_code=400),
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    with tempfile.NamedTemporaryFile("w") as writer:
        writer.write(f"{dispatch_id}")
        writer.flush()

        with open(writer.name, "rb") as reader:
            resp = client.put(
                f"/api/v2/dispatches/{dispatch_id}/electrons/{node_id}/assets/{key}", data=reader
            )

    assert resp.status_code == 400


def test_put_lattice_asset(mocker, client, test_db, mock_result_object):
    """
    Test put lattice asset
    """
    key = "workflow_function"
    dispatch_id = "test_put_lattice_asset"

    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    with tempfile.NamedTemporaryFile("w") as writer:
        writer.write(f"{dispatch_id}")
        writer.flush()

        with open(writer.name, "rb") as reader:
            resp = client.put(
                f"/api/v2/dispatches/{dispatch_id}/lattice/assets/{key}", data=reader
            )
        mock_lattice = mock_result_object.lattice
        mock_lattice.update_assets.assert_called()
        assert resp.status_code == 200


def test_put_lattice_asset_bad_dispatch_id(mocker, client):
    """
    Test put lattice asset
    """
    key = "workflow_function"
    dispatch_id = "test_put_lattice_asset_no_dispatch_id"

    mocker.patch(
        "covalent_dispatcher._service.assets.get_cached_result_object",
        side_effect=HTTPException(status_code=404),
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    with tempfile.NamedTemporaryFile("w") as writer:
        writer.write(f"{dispatch_id}")
        writer.flush()

        with open(writer.name, "rb") as reader:
            resp = client.put(
                f"/api/v2/dispatches/{dispatch_id}/lattice/assets/{key}", data=reader
            )

    assert resp.status_code == 400


def test_put_dispatch_asset(mocker, client, test_db, mock_result_object):
    """
    Test put dispatch asset
    """
    key = "result"
    dispatch_id = "test_put_dispatch_asset"

    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch(
        "covalent_dispatcher._service.assets.get_result_object", return_value=mock_result_object
    )

    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    with tempfile.NamedTemporaryFile("w") as writer:
        writer.write(f"{dispatch_id}")
        writer.flush()

        with open(writer.name, "rb") as reader:
            resp = client.put(f"/api/v2/dispatches/{dispatch_id}/assets/{key}", data=reader)
        mock_result_object.update_assets.assert_called()
        assert resp.status_code == 200


def test_put_dispatch_asset_bad_dispatch_id(mocker, client):
    """
    Test put dispatch asset
    """
    key = "result"
    dispatch_id = "test_put_dispatch_asset_no_dispatch_id"

    mocker.patch(
        "covalent_dispatcher._service.assets.get_cached_result_object",
        side_effect=HTTPException(status_code=400),
    )
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    with tempfile.NamedTemporaryFile("w") as writer:
        writer.write(f"{dispatch_id}")
        writer.flush()

        with open(writer.name, "rb") as reader:
            resp = client.put(f"/api/v2/dispatches/{dispatch_id}/assets/{key}", data=reader)

    assert resp.status_code == 400


def test_get_string_offsets():
    tobj = TransportableObject("test_get_string_offsets")

    data = tobj.serialize()
    with tempfile.NamedTemporaryFile("wb") as write_file:
        write_file.write(data)
        write_file.flush()

        start, end = _get_tobj_string_offsets(f"file://{write_file.name}")

        assert data[start:end].decode("utf-8") == tobj.object_string


def test_get_pickle_offsets():
    tobj = TransportableObject("test_get_pickle_offsets")

    data = tobj.serialize()
    with tempfile.NamedTemporaryFile("wb") as write_file:
        write_file.write(data)
        write_file.flush()

        start, end = _get_tobj_pickle_offsets(f"file://{write_file.name}")

        assert data[start:] == base64.b64decode(tobj.get_serialized().encode("utf-8"))


def test_generate_partial_file_slice():
    """Test generating slices of files."""

    data = "test_generate_file_slice".encode("utf-8")
    with tempfile.NamedTemporaryFile("wb") as write_file:
        write_file.write(data)
        write_file.flush()
        gen = _generate_file_slice(f"file://{write_file.name}", 1, 5, 2)
        assert next(gen) == data[1:3]
        assert next(gen) == data[3:5]
        with pytest.raises(StopIteration):
            next(gen)


def test_generate_whole_file_slice():
    """Test generating slices of files."""

    data = "test_generate_file_slice".encode("utf-8")
    with tempfile.NamedTemporaryFile("wb") as write_file:
        write_file.write(data)
        write_file.flush()
        gen = _generate_file_slice(f"file://{write_file.name}", 0, -1)
        assert next(gen) == data


def test_get_cached_result_obj(mocker, test_db):
    mocker.patch("covalent_dispatcher._service.assets.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._service.assets.get_result_object", side_effect=KeyError())
    with pytest.raises(HTTPException):
        get_cached_result_object("test_get_cached_result_obj")
