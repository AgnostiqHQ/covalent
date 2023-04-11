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


"""Functions to export server-side data to client"""


from sqlalchemy.orm import Session

from .electron import ASSET_KEYS as ELECTRON_ASSETS
from .electron import METADATA_KEYS as ELECTRON_META
from .lattice import ASSET_KEYS as LATTICE_ASSETS
from .lattice import METADATA_KEYS as LATTICE_META
from .result import ASSET_KEYS as RESULT_ASSETS
from .result import METADATA_KEYS as RESULT_META
from .result import get_result_object

NODE_ATTRIBUTES = ELECTRON_META.union(ELECTRON_ASSETS)
NODE_ATTRIBUTES.add("sub_dispatch_id")


LATTICE_ATTRIBUTES = LATTICE_META.union(LATTICE_ASSETS)
RESULT_ATTRIBUTES = RESULT_META.union(RESULT_ASSETS)


SDK_NODE_META_KEYS = {
    "executor",
    "executor_data",
    "deps",
    "call_before",
    "call_after",
}

SDK_LAT_META_KEYS = {
    "executor",
    "executor_data",
    "workflow_executor",
    "workflow_executor_data",
    "deps",
    "call_before",
    "call_after",
}

DEFERRED_KEYS = {
    "inputs",
    "output",
    "value",
    "result",
}

# Temporary hack for API
KEY_SUBSTITUTIONS = {"doc": "__doc__"}


def update_node_asset(session: Session, dispatch_id: str, node_id: int, key: str, values: dict):
    srv_res = get_result_object(dispatch_id, bare=True)
    node = srv_res.lattice.transport_graph.get_node(node_id)
    asset = node.get_asset(key)
    asset.update(session, values=values)


def update_lattice_asset(session: Session, dispatch_id: str, key: str, values: dict):
    srv_res = get_result_object(dispatch_id, bare=True)
    asset = srv_res.lattice.get_asset(KEY_SUBSTITUTIONS.get(key, key))
    asset.update(session, values=values)


def update_dispatch_asset(session: Session, dispatch_id: str, key: str, values: dict):
    srv_res = get_result_object(dispatch_id, bare=True)
    asset = srv_res.get_asset(key)
    asset.update(session, values=values)
