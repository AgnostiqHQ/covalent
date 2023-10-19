# Copyright 2023 Agnostiq Inc.
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


class URIFilterPolicy(enum.Enum):
    raw = "raw"  # expose raw URIs
    http = "http"  # return data endpoints


def _srv_asset_uri(
    uri: str, attrs: dict, scope: AssetScope, dispatch_id: str, node_id: Optional[int], key: str
) -> str:
    base_uri = f"{SERVER_URL}/api/v2/dispatches/{dispatch_id}"

    if scope == AssetScope.DISPATCH:
        return f"{base_uri}/assets/{key}"
    elif scope == AssetScope.LATTICE:
        return f"{base_uri}/lattice/assets/{key}"
    else:
        return f"{base_uri}/electrons/{node_id}/assets/{key}"


def _raw(
    uri: str, attrs: dict, scope: AssetScope, dispatch_id: str, node_id: Optional[int], key: str
):
    return uri


_filter_map = {
    URIFilterPolicy.raw: _raw,
    URIFilterPolicy.http: _srv_asset_uri,
}


def filter_asset_uri(
    filter_policy: URIFilterPolicy,
    uri: str,
    attrs: dict,
    scope: AssetScope,
    dispatch_id: str,
    node_id: Optional[int],
    key: str,
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

    selected_filter = _filter_map[filter_policy]
    return selected_filter(
        uri=uri,
        attrs=attrs,
        scope=scope,
        dispatch_id=dispatch_id,
        node_id=node_id,
        key=key,
    )
