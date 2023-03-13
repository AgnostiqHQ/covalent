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
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from covalent._shared_files import logger

from .._db.models import AssetMeta
from .._db.write_result_to_db import load_file, store_file
from .utils.file_transfer import cp

app_log = logger.app_log


class StorageType(Enum):
    LOCAL = "file"
    S3 = "s3"


class Asset:

    """Metadata for an object in blob storage"""

    def __init__(self, storage_path: str, object_key: str, session: Session = None):
        self.storage_type = StorageType.LOCAL
        self.storage_path = storage_path
        self.object_key = object_key

        self.meta = {}

        if session:
            meta_record = _get_meta(self, session)
            self.meta = meta_record.__dict__.copy() if meta_record else {}

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

    def _asset_id(self) -> str:
        return self.storage_path + "/" + self.object_key


def _get_meta(asset: Asset, session: Session) -> AssetMeta:
    stmt = select(AssetMeta).where(AssetMeta.asset_id == asset._asset_id())
    record = session.scalars(stmt).first()
    return record
