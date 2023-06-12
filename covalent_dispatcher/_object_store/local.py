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


import hashlib
import os
from typing import Optional, Tuple

from covalent._shared_files.config import get_config
from covalent._shared_files.schemas import electron, lattice, result

from .base import BaseProvider, Digest

BLOCK_SIZE = 65536
ALGORITHM = "sha1"

WORKFLOW_ASSET_FILENAME_MAP = result.ASSET_FILENAME_MAP.copy()
WORKFLOW_ASSET_FILENAME_MAP.update(lattice.ASSET_FILENAME_MAP)
ELECTRON_ASSET_FILENAME_MAP = electron.ASSET_FILENAME_MAP


class LocalProvider(BaseProvider):
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


local_store = LocalProvider()
