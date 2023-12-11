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

"""Tests for local object store provider"""

import tempfile

import pytest

from covalent_dispatcher._object_store.local import InvalidFileExtension, local_store


def test_store_file_invalid_extension():
    """Test the function used to write data corresponding to the filenames in the DB."""

    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(InvalidFileExtension):
            local_store.store_file(storage_path=temp_dir, filename="test.invalid", data="")

        with pytest.raises(InvalidFileExtension):
            local_store.store_file(storage_path=temp_dir, filename="test.txt", data={4})

        with pytest.raises(InvalidFileExtension):
            local_store.store_file(storage_path=temp_dir, filename="test.log", data={4})


def test_store_file_valid_extension():
    """Test the function used to write data corresponding to the filenames in the DB."""

    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(InvalidFileExtension):
            local_store.store_file(storage_path=temp_dir, filename="test.invalid", data="")

        with pytest.raises(InvalidFileExtension):
            local_store.store_file(storage_path=temp_dir, filename="test.txt", data={4})

        with pytest.raises(InvalidFileExtension):
            local_store.store_file(storage_path=temp_dir, filename="test.log", data={4})


def test_store_and_load_file():
    """Test the data storage and loading methods simultaneously."""

    with tempfile.TemporaryDirectory() as temp_dir:
        data = [1, 2, 3]
        local_store.store_file(storage_path=temp_dir, filename="pickle.pkl", data=data)
        assert local_store.load_file(storage_path=temp_dir, filename="pickle.pkl") == data

        # No file should be created in this case
        data = None
        local_store.store_file(storage_path=temp_dir, filename="pickle.txt", data=data)
        with pytest.raises(FileNotFoundError):
            assert local_store.load_file(storage_path=temp_dir, filename="pickle.txt")

        data = b"test"
        local_store.store_file(storage_path=temp_dir, filename="pickle.mdb", data=data)
        assert local_store.load_file(storage_path=temp_dir, filename="pickle.mdb") == data
