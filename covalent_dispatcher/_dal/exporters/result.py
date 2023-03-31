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


"""Functions to transform Lattice -> LatticeSchema"""


from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.schemas.asset import AssetSchema
from covalent._shared_files.schemas.result import (
    ASSET_KEYS,
    METADATA_KEYS,
    ResultAssets,
    ResultMetadata,
    ResultSchema,
)
from covalent._shared_files.utils import format_server_url
from covalent_dispatcher._dal.electron import Electron
from covalent_dispatcher._dal.result import Result

from .lattice import export_lattice

METADATA_KEYS_TO_OMIT = {"num_nodes"}
SERVER_URL = format_server_url(get_config("dispatcher.address"), get_config("dispatcher.port"))

app_log = logger.app_log


# res is assumed to represent a full db record
def _export_result_meta(res: Result) -> ResultMetadata:
    metadata_kwargs = {}
    for key in METADATA_KEYS:
        if key in METADATA_KEYS_TO_OMIT:
            continue
        metadata_kwargs[key] = res.get_value(key, None, refresh=False)

    return ResultMetadata(**metadata_kwargs)


def _populate_assets(res: Result):
    """Prepopulate the asset maps"""

    # Compute mapping from electron_id -> transport_graph_node_id

    tg = res.lattice.transport_graph
    g = tg.get_internal_graph_copy()
    all_nodes = tg.get_nodes(node_ids=list(g.nodes))

    eid_node_id_map = {node._electron_id: node.node_id for node in all_nodes}

    with res.session() as session:
        # Workflow scope
        workflow_assets = Result.get_linked_assets(
            session,
            fields=[],
            equality_filters={"id": res.metadata.primary_key},
            membership_filters={},
        )
        # Electron scope

        node_assets = Electron.get_linked_assets(
            session,
            fields=[],
            equality_filters={"parent_lattice_id": res.metadata.primary_key},
            membership_filters={},
        )

    for rec in workflow_assets:
        res.assets[rec["key"]] = rec["asset"]

    for key, val in res.assets.items():
        res.lattice.assets[key] = val

    for rec in node_assets:
        node = tg.get_node(eid_node_id_map[rec["meta_id"]])
        node.assets[rec["key"]] = rec["asset"]


def _export_result_assets(res: Result, data_uri_prefix: str) -> ResultAssets:
    manifests = {}
    for asset_key in ASSET_KEYS:
        remote_uri = data_uri_prefix + f"/{asset_key}"
        asset = res.assets[asset_key]
        manifests[asset_key] = AssetSchema(digest=asset.digest_hex, remote_uri=remote_uri)

    return ResultAssets(**manifests)


def export_result(res: Result) -> ResultSchema:
    dispatch_id = res.dispatch_id
    metadata = _export_result_meta(res)

    _populate_assets(res)

    data_uri_prefix = SERVER_URL + f"/api/v1/resultv2/{dispatch_id}/assets/dispatch"
    assets = _export_result_assets(res, data_uri_prefix)

    lat_data_uri_prefix = SERVER_URL + f"/api/v1/resultv2/{dispatch_id}/assets/lattice"
    node_data_uri_prefix = SERVER_URL + f"/api/v1/resultv2/{dispatch_id}/assets/node"
    lattice = export_lattice(res.lattice, lat_data_uri_prefix, node_data_uri_prefix)

    return ResultSchema(metadata=metadata, assets=assets, lattice=lattice)
