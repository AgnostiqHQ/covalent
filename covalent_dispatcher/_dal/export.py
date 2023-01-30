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


"""Functions to export server-side data to client"""

from pathlib import Path
from typing import Dict

from covalent._workflow.lattice import Lattice as SDKLattice
from covalent._workflow.transport import _TransportGraph as SDKGraph

from .electron import ASSET_KEYS as ELECTRON_ASSETS
from .electron import METADATA_KEYS as ELECTRON_META
from .lattice import ASSET_KEYS as LATTICE_ASSETS
from .lattice import METADATA_KEYS as LATTICE_META
from .lattice import Lattice as SRVLattice
from .result import ASSET_KEYS as RESULT_ASSETS
from .result import METADATA_KEYS as RESULT_META
from .result import Result as SRVResult
from .result import get_result_object
from .tg import _TransportGraph as SRVGraph
from .tg import get_compute_graph

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

# Functions to support get_result


def _to_client_graph(srv_graph: SRVGraph) -> SDKGraph:
    sdk_graph = SDKGraph()

    sdk_graph._graph = srv_graph.get_internal_graph_copy()
    for node_id in srv_graph._graph.nodes:
        attributes = {}
        for k in NODE_ATTRIBUTES:
            if k not in DEFERRED_KEYS and k not in SDK_NODE_META_KEYS:
                attributes[k] = srv_graph.get_node_value(node_id, k)
        if srv_graph.get_node_value(node_id, "type") == "parameter":
            attributes["value"] = srv_graph.get_node_value(node_id, "value")

        node_meta = {k: srv_graph.get_node_value(node_id, k) for k in SDK_NODE_META_KEYS}
        attributes["metadata"] = node_meta
        for k, v in attributes.items():
            sdk_graph.set_node_value(node_id, k, v)

        sdk_graph.lattice_metadata = {}

    return sdk_graph


def _to_client_lattice(srv_lat: SRVLattice) -> SDKLattice:
    def dummy(x):
        return x

    sdk_lat = SDKLattice(dummy)
    for k in LATTICE_ATTRIBUTES:
        if k not in DEFERRED_KEYS and k not in SDK_LAT_META_KEYS:
            setattr(sdk_lat, k, srv_lat.get_value(k))
    lat_meta = {k: srv_lat.get_value(k) for k in SDK_LAT_META_KEYS}
    sdk_lat.metadata = lat_meta

    # Load transport graph
    srv_graph = get_compute_graph(srv_lat._lattice_id)

    sdk_lat.transport_graph = _to_client_graph(srv_graph)

    sdk_lat.transport_graph.lattice_metadata = sdk_lat.metadata

    return sdk_lat


def _to_serialized_client_result(result: SRVResult) -> Dict:
    result_attrs = {}
    for k in RESULT_ATTRIBUTES:
        if k not in DEFERRED_KEYS:
            result_attrs[k] = result.get_value(k)

    # Serialize attributes to JSON compatible format

    result_attrs["status"] = str(result_attrs["status"])
    if result_attrs["start_time"]:
        result_attrs["start_time"] = result_attrs["start_time"].isoformat()

    if result_attrs["end_time"]:
        result_attrs["end_time"] = result_attrs["end_time"].isoformat()

    sdk_lat = _to_client_lattice(result.lattice)

    return {
        "result": result_attrs,
        "lattice": sdk_lat.serialize_to_json(),
    }


def export_serialized_result(dispatch_id: str) -> Dict:
    srv_res = get_result_object(dispatch_id)
    return _to_serialized_client_result(srv_res)


def get_node_asset_uri(dispatch_id: str, node_id: int, key: str) -> str:
    srv_res = get_result_object(dispatch_id, bare=True)
    node = srv_res.lattice.transport_graph.get_node(node_id)
    asset = node.get_asset(key)

    return str(Path(asset.storage_path) / asset.object_key)


def get_lattice_asset_uri(dispatch_id: str, key: str) -> str:
    srv_res = get_result_object(dispatch_id, bare=True)
    asset = srv_res.lattice.get_asset(key)
    return str(Path(asset.storage_path) / asset.object_key)


def get_dispatch_asset_uri(dispatch_id: str, key: str) -> str:
    srv_res = get_result_object(dispatch_id, bare=True)
    asset = srv_res.get_asset(key)
    return str(Path(asset.storage_path) / asset.object_key)
