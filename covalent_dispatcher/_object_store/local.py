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


import hashlib
import json
import os
from pathlib import Path
from typing import Any, Optional, Tuple

import cloudpickle

from covalent._shared_files.config import get_config
from covalent._shared_files.schemas import electron, lattice, result
from covalent._workflow.transport import TransportableObject

from .base import BaseProvider, Digest

BLOCK_SIZE = 65536
ALGORITHM = "sha1"

WORKFLOW_ASSET_FILENAME_MAP = result.ASSET_FILENAME_MAP.copy()
WORKFLOW_ASSET_FILENAME_MAP.update(lattice.ASSET_FILENAME_MAP)
ELECTRON_ASSET_FILENAME_MAP = electron.ASSET_FILENAME_MAP.copy()


# Moved from write_result_to_db.py


class InvalidFileExtension(Exception):
    """
    Exception to raise when an invalid file extension is encountered
    """

    pass


class LocalProvider(BaseProvider):
    scheme = "file"

    def __init__(self):
        self.base_path = get_config("dispatcher.results_dir")

    def digest(self, bucket_name: str, object_key: str) -> Digest:
        path = os.path.join(bucket_name, object_key)
        h = hashlib.new(ALGORITHM)
        with open(path, "rb") as f:
            buf = f.read(BLOCK_SIZE)
            while len(buf) > 0:
                h.update(buf)
                buf = f.read(BLOCK_SIZE)

        return Digest(algorithm=ALGORITHM, hexdigest=h.hexdigest())

    def size(self, bucket_name: str, object_key: str) -> int:
        path = os.path.join(bucket_name, object_key)

        try:
            return os.path.size(path)
        except OSError:
            return 0

    def get_uri_components(
        self, dispatch_id: str, node_id: Optional[int], asset_key: str
    ) -> Tuple[str, str]:
        """Compute storage_path and object_key for a workflow asset.

        Args:
            dispatch_id: The workflow dispatch id
            node_id: The electron's node id or `None` if the asset has workflow scope.
            asset_key: The key describing the asset.

        Returns:
            storage_path, object_key

        The semantics `storage_path` and `object_key` may differ
        slightly between backends but are constrained by the requirement that
        `{scheme}://{storage_path}/{object_key}` is a valid URI for
        the asset.

        """
        storage_path = os.path.join(self.base_path, dispatch_id)

        if node_id is not None:
            storage_path = os.path.join(storage_path, f"node_{node_id}")
            object_key = ELECTRON_ASSET_FILENAME_MAP[asset_key]
        else:
            object_key = WORKFLOW_ASSET_FILENAME_MAP[asset_key]

        os.makedirs(storage_path, exist_ok=True)

        return storage_path, object_key

    def store_file(self, storage_path: str, filename: str, data: Any = None) -> Digest:
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

        elif filename.endswith(".tobj"):
            with open(Path(storage_path) / filename, "wb") as f:
                f.write(data.serialize())

        elif filename.endswith(".json"):
            with open(Path(storage_path) / filename, "w") as f:
                json.dump(data, f)

        elif filename.endswith(".mdb"):
            with open(Path(storage_path) / filename, "wb") as f:
                f.write(data)
        else:
            raise InvalidFileExtension("The file extension is not supported.")

        digest = self.digest(bucket_name=storage_path, object_key=filename)
        return digest

    def load_file(self, storage_path: str, filename: str) -> Any:
        """This function loads data for the filenames in the DB."""

        if filename.endswith(".pkl"):
            with open(Path(storage_path) / filename, "rb") as f:
                data = cloudpickle.load(f)

        elif filename.endswith(".log") or filename.endswith(".txt"):
            with open(Path(storage_path) / filename, "r") as f:
                data = f.read()

        elif filename.endswith(".tobj"):
            with open(Path(storage_path) / filename, "rb") as f:
                data = TransportableObject.deserialize(f.read())

        elif filename.endswith(".json"):
            with open(Path(storage_path) / filename, "r") as f:
                data = json.load(f)

        elif filename.endswith(".mdb"):
            with open(Path(storage_path) / filename, "rb") as f:
                data = f.read()

        return data


local_store = LocalProvider()
