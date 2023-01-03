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

from enum import Enum
from typing import Any

from .._db.write_result_to_db import load_file, store_file


class StorageType(Enum):
    LOCAL = "file"
    S3 = "s3"


class Asset:

    """Metadata for an object in blob storage"""

    def __init__(self, storage_path: str, object_key: str):
        self.storage_type = StorageType.LOCAL
        self.storage_path = storage_path
        self.object_key = object_key

        self.remote_uri = ""

    def set_remote(self, uri: str) -> "Asset":
        self.remote_uri = uri
        return self

    def store_data(self, data: Any) -> None:
        store_file(self.storage_path, self.object_key, data)

    def load_data(self) -> Any:
        return load_file(self.storage_path, self.object_key)
