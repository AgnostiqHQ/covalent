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

""" Tests for qelectron's Database class """


import tempfile

import pytest

from covalent.quantum.qserver.database import Database


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def db(temp_dir):
    return Database(db_dir=temp_dir)


@pytest.mark.parametrize("direct_path", [True, False])
@pytest.mark.parametrize("mkdir", [True, False])
def test_get_db_path(mocker, db, direct_path, mkdir):
    """Test the function used to get the path to the database."""

    db.db_dir = mocker.Mock()

    db_path = db.get_db_path(direct_path=direct_path, mkdir=mkdir)

    if direct_path:
        assert db_path == db.db_dir.resolve.return_value.absolute.return_value

    else:
        db.db_dir.joinpath.assert_called_once_with("default-dispatch", "node-default-node")
        assert (
            db_path == db.db_dir.joinpath.return_value.resolve.return_value.absolute.return_value
        )

        if mkdir:
            db.db_dir.joinpath.return_value.mkdir.assert_called_once_with(
                parents=True, exist_ok=True
            )
        else:
            db.db_dir.joinpath.return_value.mkdir.assert_not_called()


@pytest.mark.parametrize("direct_path", [True, False])
@pytest.mark.parametrize("mkdir", [True, False])
@pytest.mark.parametrize("db_path_exists", [True, False])
def test_open(mocker, db, direct_path, mkdir, db_path_exists):
    """Test the function used to open a database."""

    mock_dispatch_id = "mock-dispatch-id"
    mock_node_id = "mock-node-id"

    mock_get_db_path = mocker.patch.object(db, "get_db_path")
    mock_get_db_path.return_value = mocker.Mock()
    mock_get_db_path.return_value.exists.return_value = db_path_exists

    mock_json_lmdb = mocker.patch("covalent.quantum.qserver.database.JsonLmdb")

    if not db_path_exists:
        with pytest.raises(FileNotFoundError):
            db._open(
                dispatch_id=mock_dispatch_id,
                node_id=mock_node_id,
                direct_path=direct_path,
                mkdir=mkdir,
            )
            mock_get_db_path.return_value.exists.assert_called_once_with()
            assert mock_json_lmdb.open_with_strategy.call_count == 0
        return

    db._open(
        dispatch_id=mock_dispatch_id, node_id=mock_node_id, direct_path=direct_path, mkdir=mkdir
    )

    mock_get_db_path.assert_called_once_with(
        mock_dispatch_id, mock_node_id, direct_path=direct_path, mkdir=mkdir
    )

    mock_json_lmdb.open_with_strategy.assert_called_once_with(
        file=str(mock_get_db_path.return_value),
        flag="c",
        strategy_name=Database.serialization_strategy,
    )


@pytest.mark.parametrize("direct_path", [True, False])
def test_set(mocker, db, direct_path):
    """Test the function used to set data in the database."""

    mock_open = mocker.patch.object(db, "_open")
    mock_open.return_value.__enter__.return_value = mocker.Mock()

    mock_keys = ["key1", "key2"]
    mock_values = ["value1", "value2"]
    mock_dispatch_id = "mock-dispatch-id"
    mock_node_id = "mock-node-id"

    db.set(
        keys=mock_keys,
        values=mock_values,
        dispatch_id=mock_dispatch_id,
        node_id=mock_node_id,
        direct_path=direct_path,
    )

    mock_open.assert_called_once_with(
        mock_dispatch_id, mock_node_id, direct_path=direct_path, mkdir=True
    )

    mock_open.return_value.__enter__.return_value.update.assert_called_once_with(
        dict(zip(mock_keys, mock_values))
    )


@pytest.mark.parametrize("direct_path", [True, False])
def test_get_circuit_ids(mocker, db, direct_path):
    """Test the function used to get circuit IDs from the database."""

    mock_open = mocker.patch.object(db, "_open")
    mock_open.return_value.__enter__.return_value = mocker.Mock()
    mock_open.return_value.__enter__.return_value.keys.return_value = ["key1", "key2"]

    mock_dispatch_id = "mock-dispatch-id"
    mock_node_id = "mock-node-id"

    circuit_ids = db.get_circuit_ids(
        dispatch_id=mock_dispatch_id, node_id=mock_node_id, direct_path=direct_path
    )

    mock_open.assert_called_once_with(mock_dispatch_id, mock_node_id, direct_path=direct_path)

    mock_open.return_value.__enter__.return_value.keys.assert_called_once_with()

    assert circuit_ids == list(mock_open.return_value.__enter__.return_value.keys.return_value)


@pytest.mark.parametrize("direct_path", [True, False])
def test_get_circuit_info(mocker, db, direct_path):
    """Test the function used to get circuit info from the database."""

    mock_circuit_info_class = mocker.patch("covalent.quantum.qserver.database.CircuitInfo")

    mock_open = mocker.patch.object(db, "_open")
    mock_open.return_value.__enter__.return_value = mocker.Mock()
    mock_open.return_value.__enter__.return_value.get.return_value = {"key1": "value1"}

    mock_dispatch_id = "mock-dispatch-id"
    mock_node_id = "mock-node-id"
    mock_circuit_id = "mock-circuit-id"

    db.get_circuit_info(
        circuit_id=mock_circuit_id,
        dispatch_id=mock_dispatch_id,
        node_id=mock_node_id,
        direct_path=direct_path,
    )

    mock_open.assert_called_once_with(mock_dispatch_id, mock_node_id, direct_path=direct_path)

    mock_open.return_value.__enter__.return_value.get.assert_called_once_with(
        mock_circuit_id, None
    )

    mock_circuit_info_class.assert_called_once_with(
        **mock_open.return_value.__enter__.return_value.get.return_value
    )


@pytest.mark.parametrize("direct_path", [True, False])
def test_get_db_dict(mocker, db, direct_path):
    """Test the function used to get the database as a dictionary."""

    mock_open = mocker.patch.object(db, "_open")
    mock_open.return_value.__enter__.return_value = mocker.Mock()
    mock_open.return_value.__enter__.return_value.items.return_value = [
        ("key1", "value1"),
        ("key2", "value2"),
    ]

    mock_dispatch_id = "mock-dispatch-id"
    mock_node_id = "mock-node-id"

    db_dict = db.get_db_dict(
        dispatch_id=mock_dispatch_id, node_id=mock_node_id, direct_path=direct_path
    )

    mock_open.assert_called_once_with(mock_dispatch_id, mock_node_id, direct_path=direct_path)

    mock_open.return_value.__enter__.return_value.items.assert_called_once_with()

    assert db_dict == dict(mock_open.return_value.__enter__.return_value.items.return_value)
