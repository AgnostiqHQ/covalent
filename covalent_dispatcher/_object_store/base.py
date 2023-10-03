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

"""Base storage backend provider"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Digest:
    algorithm: str
    hexdigest: str


class BaseProvider:
    @classmethod
    @property
    def scheme(cls) -> str:
        raise NotImplementedError

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
