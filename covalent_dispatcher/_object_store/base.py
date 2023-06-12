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

"""Base storage backend provider"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Digest:
    algorithm: str
    hexdigest: str


class BaseProvider:
    def digest(self, bucket_name: str, object_key: str) -> Digest:
        raise NotImplementedError

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

        raise NotImplementedError
