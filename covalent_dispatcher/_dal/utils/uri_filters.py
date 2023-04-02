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

"""Functions to transform URIs"""

import enum
from typing import Optional

from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.utils import format_server_url

SERVER_URL = format_server_url(get_config("dispatcher.address"), get_config("dispatcher.port"))

app_log = logger.app_log


class AssetScope(enum.Enum):
    DISPATCH = "dispatch"
    LATTICE = "lattice"
    NODE = "node"


class AccessType(enum.Enum):
    READ = "READ"
    WRITE = "WRITE"


def _srv_asset_uri(scope: AssetScope, dispatch_id: str, node_id: Optional[int], key: str) -> str:
    base_uri = SERVER_URL + f"/api/v1/resultv2/{dispatch_id}/assets/{scope.value}"

    if scope == AssetScope.DISPATCH or scope == AssetScope.LATTICE:
        uri = base_uri + f"/{key}"
    else:
        uri = base_uri + f"/{node_id}/{key}"
    return uri


def filter_asset_uri(
    uri: str, attrs: dict, scope: AssetScope, dispatch_id: str, node_id: Optional[int], key: str
) -> str:
    """Transform an internal URI for an asset to an external URI.

    Parameters:
        uri: internal URI
        attrs: attributes for the external URI
        scope: asset scope ("dispatch", "lattice", "node")
        key: asset key

    Returns:
        The external URI for the asset

    """
    output_uri = _srv_asset_uri(scope, dispatch_id, node_id, key)
    app_log.debug(f"transformed {uri} -> {output_uri}")
    return output_uri
