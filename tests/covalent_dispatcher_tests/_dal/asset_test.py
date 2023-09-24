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

"""Tests for Asset"""

import os
import tempfile

import pytest

from covalent_dispatcher._dal.asset import FIELDS, Asset, StorageType, copy_asset, copy_asset_meta
from covalent_dispatcher._db import models
from covalent_dispatcher._db.datastore import DataStore


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def get_asset_record(storage_path, object_key, digest_alg="", digest="", size=0):
    return models.Asset(
        storage_type=StorageType.LOCAL.value,
        storage_path=storage_path,
        object_key=object_key,
        digest_alg=digest_alg,
        digest=digest,
        size=size,
    )


def test_asset_load_data():
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as temp:
        temp.write("Hello\n")
        temppath = temp.name
        key = os.path.basename(temppath)

    storage_path = "/tmp"

    rec = get_asset_record(storage_path, key)
    a = Asset(None, rec)
    assert a.load_data() == "Hello\n"
    os.unlink(temppath)


def test_asset_store_data():
    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        temppath = temp.name
        key = os.path.basename(temppath)
    storage_path = "/tmp"
    rec = get_asset_record(storage_path, key)
    a = Asset(None, rec)
    a.store_data("Hello\n")

    with open(temppath, "r") as f:
        assert f.read() == "Hello\n"

    os.unlink(temppath)


def test_upload_asset():
    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        src_path = temp.name
        src_key = os.path.basename(src_path)
    storage_path = "/tmp"

    rec = get_asset_record(storage_path, src_key)
    a = Asset(None, rec)
    a.store_data("Hello\n")

    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        dest_path = temp.name
        dest_key = os.path.basename(dest_path)

    a.upload(dest_path)

    with open(dest_path, "r") as f:
        assert f.read() == "Hello\n"
    os.unlink(dest_path)


def test_download_asset():
    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        src_path = temp.name
        src_key = os.path.basename(src_path)
    with open(src_path, "w") as f:
        f.write("Hello\n")

    storage_path = "/tmp"
    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        dest_path = temp.name
        dest_key = os.path.basename(dest_path)

    rec = get_asset_record(storage_path, dest_key)
    a = Asset(None, rec)

    a.download(src_path)

    assert a.load_data() == "Hello\n"

    os.unlink(dest_path)


def test_copy_asset():
    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        src_path = temp.name
        src_key = os.path.basename(src_path)
    with open(src_path, "w") as f:
        f.write("Hello\n")

    storage_path = "/tmp"
    rec = get_asset_record(storage_path, src_key)
    src_asset = Asset(None, rec)

    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        dest_path = temp.name
        dest_key = os.path.basename(dest_path)

    rec = get_asset_record(storage_path, dest_key)
    dest_asset = Asset(None, rec)

    copy_asset(src_asset, dest_asset)

    assert dest_asset.load_data() == "Hello\n"


def test_copy_asset_metadata(test_db):
    src_rec = get_asset_record("/tmp", "src_key", "sha", "srcdigest", 256)
    dest_rec = get_asset_record("/tmp", "dest_key")

    with test_db.session() as session:
        session.add(src_rec)
        session.add(dest_rec)

    with test_db.session():
        session.add(src_rec)
        session.add(dest_rec)
        src_asset = Asset(None, src_rec)
        dest_asset = Asset(None, dest_rec)
        copy_asset_meta(session, src_asset, dest_asset)

    with test_db.session() as session:
        dest_asset.refresh(session, fields=FIELDS)

        assert dest_asset.digest_alg == "sha"
        assert dest_asset.digest == "srcdigest"
        assert dest_asset.size == 256
