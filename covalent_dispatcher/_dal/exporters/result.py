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


"""Functions to transform Lattice -> LatticeSchema"""


from covalent._shared_files import logger
from covalent._shared_files.schemas.asset import AssetSchema
from covalent._shared_files.schemas.result import (
    ASSET_KEYS,
    METADATA_KEYS,
    ResultAssets,
    ResultMetadata,
    ResultSchema,
)
from covalent_dispatcher._dal.electron import Electron
from covalent_dispatcher._dal.result import Result, get_result_object
from covalent_dispatcher._object_store.base import TransferDirection

from .lattice import export_lattice

METADATA_KEYS_TO_OMIT = {"num_nodes"}

app_log = logger.app_log


# res is assumed to represent a full db record
def _export_result_meta(res: Result) -> ResultMetadata:
    metadata_kwargs = {
        key: res.get_metadata(key, None, refresh=False)
        for key in METADATA_KEYS
        if key not in METADATA_KEYS_TO_OMIT
    }
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


def _export_result_assets(res: Result) -> ResultAssets:
    manifests = {}
    for asset_key in ASSET_KEYS:
        asset = res.assets[asset_key]
        size = asset.size
        digest_alg = asset.digest_alg
        digest = asset.digest
        object_store = asset.object_store
        remote_uri = object_store.get_public_uri(
            asset.storage_path,
            asset.object_key,
            transfer_direction=TransferDirection.download,
        )
        manifests[asset_key] = AssetSchema(
            remote_uri=remote_uri, size=size, digest_alg=digest_alg, digest=digest
        )

    return ResultAssets(**manifests)


def export_result(res: Result) -> ResultSchema:
    """Export a Result object"""
    dispatch_id = res.dispatch_id
    metadata = _export_result_meta(res)

    _populate_assets(res)

    assets = _export_result_assets(res)
    lattice = export_lattice(res.lattice)

    # Filter asset URIs

    return ResultSchema(metadata=metadata, assets=assets, lattice=lattice)


def export_result_manifest(dispatch_id: str) -> ResultSchema:
    srv_res = get_result_object(dispatch_id, bare=False)
    return export_result(srv_res)
