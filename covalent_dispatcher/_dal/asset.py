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

"""Asset class and utility functions"""

import os
from enum import Enum
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from covalent._shared_files import logger

from .._db.models import Asset as AssetRecord
from .._object_store.local import BaseProvider, local_store
from .controller import Record
from .utils.file_transfer import cp

app_log = logger.app_log


class StorageType(Enum):
    LOCAL = "file"
    S3 = "s3"


_storage_provider_map = {
    StorageType.LOCAL: local_store,
}


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
    def object_store(self) -> BaseProvider:
        return _storage_provider_map[self.storage_type]

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

    def set_remote(self, session: Session, uri: str):
        self.update(session, values={"remote_uri": uri})

    def store_data(self, data: Any) -> None:
        self.object_store.store_file(self.storage_path, self.object_key, data)

    def load_data(self) -> Any:
        return self.object_store.load_file(self.storage_path, self.object_key)

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


def copy_asset(src: Asset, dest: Asset):
    """Copy the data for an asset.

    Args:
        session: SQLalchemy session
        src: The source asset
        dest The destination asset
    """

    scheme = dest.storage_type.value
    dest_uri = scheme + "://" + os.path.join(dest.storage_path, dest.object_key)
    src.upload(dest_uri)


def copy_asset_meta(session: Session, src: Asset, dest: Asset):
    """Copy the metadata for an asset.

    Args:
        session: SQLalchemy session
        src: The source asset
        dest The destination asset
    """

    update = {
        "digest_alg": src.digest_alg,
        "digest": src.digest,
        "size": src.size,
    }
    dest.update(session, values=update)
