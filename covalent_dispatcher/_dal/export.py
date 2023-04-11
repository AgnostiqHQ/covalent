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

from typing import Dict

from sqlalchemy.orm import Session

from covalent._shared_files.schemas.result import ResultSchema
from covalent._workflow.lattice import Lattice as SDKLattice
from covalent._workflow.transport import _TransportGraph as SDKGraph

from .asset import Asset
from .electron import ASSET_KEYS as ELECTRON_ASSETS
from .electron import METADATA_KEYS as ELECTRON_META
from .exporters.result import export_result
from .lattice import ASSET_KEYS as LATTICE_ASSETS
from .lattice import METADATA_KEYS as LATTICE_META
from .lattice import Lattice as SRVLattice
from .result import ASSET_KEYS as RESULT_ASSETS
from .result import METADATA_KEYS as RESULT_META
from .result import Result as SRVResult
from .result import get_result_object
from .tg import _TransportGraph as SRVGraph

NODE_ATTRIBUTES = ELECTRON_META.union(ELECTRON_ASSETS)
NODE_ATTRIBUTES.add("sub_dispatch_id")


LATTICE_ATTRIBUTES = LATTICE_META.union(LATTICE_ASSETS)
RESULT_ATTRIBUTES = RESULT_META.union(RESULT_ASSETS)

local_scheme_prefix = "file://"

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


# Functions to support get_result


def _to_client_graph(srv_graph: SRVGraph) -> SDKGraph:
    sdk_graph = SDKGraph()

    sdk_graph._graph = srv_graph.get_internal_graph_copy()
    for node_id in srv_graph._graph.nodes:
        attrs = list(sdk_graph._graph.nodes[node_id].keys())
        for k in attrs:
            del sdk_graph._graph.nodes[node_id][k]
        attributes = {}
        for k in NODE_ATTRIBUTES:
            if k not in DEFERRED_KEYS and k not in SDK_NODE_META_KEYS:
                attributes[k] = srv_graph.get_node_value(node_id, k)
        if srv_graph.get_node_value(node_id, "type") == "parameter":
            attributes["value"] = srv_graph.get_node_value(node_id, "value")
            attributes["output"] = srv_graph.get_node_value(node_id, "output")

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
    srv_graph = SRVGraph.get_compute_graph(srv_lat._lattice_id)

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


def export_result_manifest(dispatch_id: str) -> ResultSchema:
    srv_res = get_result_object(dispatch_id, bare=False)
    return export_result(srv_res)


def get_node_asset(session: Session, dispatch_id: str, node_id: int, key: str) -> Asset:
    srv_res = get_result_object(dispatch_id, bare=True)
    node = srv_res.lattice.transport_graph.get_node(node_id)
    return node.get_asset(key)


def get_node_asset_path(session: Session, dispatch_id: str, node_id: int, key: str) -> str:
    asset = get_node_asset(session, dispatch_id, node_id, key)
    return asset.internal_uri[len(local_scheme_prefix) :]


def get_lattice_asset(session: Session, dispatch_id: str, key: str) -> Asset:
    srv_res = get_result_object(dispatch_id, bare=True)
    return srv_res.lattice.get_asset(KEY_SUBSTITUTIONS.get(key, key))


def get_lattice_asset_path(session: Session, dispatch_id: str, key: str) -> str:
    asset = get_lattice_asset(session, dispatch_id, key)
    return asset.internal_uri[len(local_scheme_prefix) :]


def get_dispatch_asset(session: Session, dispatch_id: str, key: str) -> Asset:
    srv_res = get_result_object(dispatch_id, bare=True)
    return srv_res.get_asset(key)


def get_dispatch_asset_path(session: Session, dispatch_id: str, key: str) -> str:
    asset = get_dispatch_asset(session, dispatch_id, key)
    return asset.internal_uri[len(local_scheme_prefix) :]
