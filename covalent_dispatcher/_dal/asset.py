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

"""Asset class and utility functions"""

import os
from enum import Enum
from pathlib import Path
from typing import Any

import cloudpickle
from sqlalchemy.orm import Session

from covalent._shared_files import logger

from .._db.models import Asset as AssetRecord
from .._object_store.local import Digest, local_store
from .controller import Record
from .utils.file_transfer import cp

app_log = logger.app_log


class StorageType(Enum):
    LOCAL = "file"
    S3 = "s3"


FIELDS = {
    "id",
    "storage_type",
    "storage_path",
    "object_key",
    "digest_alg",
    "digest",
    "remote_uri",
    "size",
}


class Asset(Record[AssetRecord]):

    """Metadata for an object in blob storage"""

    model = AssetRecord

    def __init__(self, session: Session, record: AssetRecord, *, keys: list = FIELDS):
        self._id = record.id
        self._attrs = {k: getattr(record, k) for k in keys}

    @property
    def primary_key(self):
        return self._id

    @property
    def storage_type(self) -> StorageType:
        return StorageType(self._attrs["storage_type"])

    @property
    def storage_path(self) -> str:
        return self._attrs["storage_path"]

    @property
    def object_key(self) -> str:
        return self._attrs["object_key"]

    @property
    def digest_alg(self) -> str:
        return self._attrs["digest_alg"]

    @property
    def digest(self) -> str:
        return self._attrs["digest"]

    @property
    def remote_uri(self) -> str:
        return self._attrs["remote_uri"]

    @property
    def internal_uri(self) -> str:
        scheme = self.storage_type.value
        return f"{scheme}://" + str(Path(self.storage_path) / self.object_key)

    @property
    def size(self) -> int:
        return self._attrs["size"]

    def store_data(self, data: Any) -> None:
        store_file(self.storage_path, self.object_key, data)

    def load_data(self) -> Any:
        return load_file(self.storage_path, self.object_key)

    def download(self, src_uri: str):
        scheme = self.storage_type.value
        dest_uri = scheme + "://" + os.path.join(self.storage_path, self.object_key)
        app_log.debug(f"Downloading asset from {src_uri} to {dest_uri}")

        cp(src_uri, dest_uri)

    def upload(self, dest_uri: str):
        scheme = self.storage_type.value
        src_uri = scheme + "://" + os.path.join(self.storage_path, self.object_key)
        app_log.debug(f"Uploading asset from {src_uri} to {dest_uri}")
        cp(src_uri, dest_uri)

    @classmethod
    def from_id(cls, asset_id: int, session: Session, *, keys=FIELDS) -> "Asset":
        records = cls.get(
            session, fields=keys, equality_filters={"id": asset_id}, membership_filters={}
        )
        record = records[0]
        return Asset(session, record, keys=keys)


# Moved from write_result_to_db.py


class InvalidFileExtension(Exception):
    """
    Exception to raise when an invalid file extension is encountered
    """

    pass


def store_file(storage_path: str, filename: str, data: Any = None) -> Digest:
    """This function writes data corresponding to the filepaths in the DB."""

    if filename.endswith(".pkl"):
        with open(Path(storage_path) / filename, "wb") as f:
            cloudpickle.dump(data, f)

    elif filename.endswith(".log") or filename.endswith(".txt"):
        if data is None:
            data = ""

        if not isinstance(data, str):
            raise InvalidFileExtension("Data must be string type.")

        with open(Path(storage_path) / filename, "w+") as f:
            f.write(data)

    else:
        raise InvalidFileExtension("The file extension is not supported.")

    digest = local_store.digest(bucket_name=storage_path, object_key=filename)
    return digest


def load_file(storage_path: str, filename: str) -> Any:
    """This function loads data for the filenames in the DB."""

    if filename.endswith(".pkl"):
        with open(Path(storage_path) / filename, "rb") as f:
            data = cloudpickle.load(f)

    elif filename.endswith(".log") or filename.endswith(".txt"):
        with open(Path(storage_path) / filename, "r") as f:
            data = f.read()

    return data
