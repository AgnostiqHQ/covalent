# Copyright 2023 Agnostiq Inc.
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

        data = None
        local_store.store_file(storage_path=temp_dir, filename="pickle.txt", data=data)
        assert local_store.load_file(storage_path=temp_dir, filename="pickle.txt") == ""
