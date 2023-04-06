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

"""Functions to convert lattice -> LatticeSchema"""


from .._results_manager.result import Result
from .._shared_files.schemas.lattice import (
    LATTICE_ERROR_FILENAME,
    LATTICE_INPUTS_FILENAME,
    LATTICE_RESULTS_FILENAME,
)
from .._shared_files.schemas.result import ResultAssets, ResultMetadata, ResultSchema
from .._shared_files.util_classes import Status
from .common import AssetType, load_asset, save_asset
from .lattice import deserialize_lattice, serialize_lattice

ASSET_TYPES = {
    "inputs": AssetType.OBJECT,
    "error": AssetType.TEXT,
    "result": AssetType.TRANSPORTABLE,
}


ASSET_FILENAME_MAP = {
    "inputs": LATTICE_INPUTS_FILENAME,
    "result": LATTICE_RESULTS_FILENAME,
    "error": LATTICE_ERROR_FILENAME,
}


def _serialize_result_metadata(res: Result) -> ResultMetadata:
    return ResultMetadata(
        dispatch_id=res._dispatch_id,
        root_dispatch_id=res._root_dispatch_id,
        status=str(res._status),
    )


def _deserialize_result_metadata(meta: ResultMetadata) -> dict:
    return {
        "_dispatch_id": meta.dispatch_id,
        "_root_dispatch_id": meta.root_dispatch_id,
        "_status": Status(meta.status),
    }


def _serialize_result_assets(res: Result, storage_path: str) -> ResultAssets:
    # NOTE: We can avoid pickling here since the UI actually consumes only the string representation
    inputs_asset = save_asset(
        res._inputs, ASSET_TYPES["inputs"], storage_path, ASSET_FILENAME_MAP["inputs"]
    )

    error_asset = save_asset(
        res._error, ASSET_TYPES["error"], storage_path, ASSET_FILENAME_MAP["error"]
    )
    result_asset = save_asset(
        res._result,
        ASSET_TYPES["result"],
        storage_path,
        ASSET_FILENAME_MAP["result"],
    )
    return ResultAssets(inputs=inputs_asset, result=result_asset, error=error_asset)


def _deserialize_result_assets(assets: ResultAssets) -> dict:
    error = load_asset(assets.error, AssetType.TEXT)
    result = load_asset(assets.result, AssetType.TRANSPORTABLE)
    inputs = load_asset(assets.inputs, AssetType.OBJECT)
    return {"_result": result, "_error": error, "_inputs": inputs}


def serialize_result(res: Result, storage_path: str) -> ResultSchema:
    meta = _serialize_result_metadata(res)
    assets = _serialize_result_assets(res, storage_path)
    lat = serialize_lattice(res.lattice, storage_path)
    return ResultSchema(metadata=meta, assets=assets, lattice=lat)


def deserialize_result(res: ResultSchema) -> Result:
    dispatch_id = res.metadata.dispatch_id
    lat = deserialize_lattice(res.lattice)
    result_object = Result(lat, dispatch_id)
    attrs = _deserialize_result_metadata(res.metadata)
    assets = _deserialize_result_assets(res.assets)

    attrs.update(assets)
    result_object.__dict__.update(attrs)
    return result_object


# Functions to preprocess manifest for submission


def strip_local_uris(res: ResultSchema) -> ResultSchema:
    # Create a copy with the local uris removed for submission
    manifest = res.copy(deep=True).dict()

    # Strip workflow asset uris:
    dispatch_assets = manifest["assets"]
    for _, asset in dispatch_assets.items():
        asset["uri"] = ""

    lattice = manifest["lattice"]
    lattice_assets = lattice["assets"]
    for _, asset in lattice_assets.items():
        asset["uri"] = ""

    # Node assets
    tg = lattice["transport_graph"]

    nodes = tg["nodes"]
    for node in nodes:
        node_assets = node["assets"]
        for _, asset in node_assets.items():
            asset["uri"] = ""

    return ResultSchema.parse_obj(manifest)


# Functions to postprocess response


def merge_response_manifest(res: ResultSchema, response: ResultSchema) -> ResultSchema:
    res.metadata.dispatch_id = response.metadata.dispatch_id
    res.metadata.root_dispatch_id = response.metadata.root_dispatch_id

    # Strip workflow asset uris:
    dispatch_assets = response.assets
    for key, asset in res.assets:
        remote_asset = getattr(dispatch_assets, key)
        asset.remote_uri = remote_asset.remote_uri

    lattice = response.lattice
    lattice_assets = lattice.assets
    for key, asset in res.lattice.assets:
        remote_asset = getattr(lattice_assets, key)
        asset.remote_uri = remote_asset.remote_uri

    # Node assets
    tg = lattice.transport_graph

    # Sort returned nodes b/c task packing may reorder nodes
    tg.nodes.sort(key=lambda x: x.id)
    nodes = res.lattice.transport_graph.nodes

    for i, node in enumerate(nodes):
        returned_node = tg.nodes[i]
        returned_node_assets = returned_node.assets
        for key, asset in node.assets:
            remote_asset = getattr(returned_node_assets, key)
            asset.remote_uri = remote_asset.remote_uri
    return res


def extract_assets(manifest: dict) -> list:
    assets = []

    # workflow-level assets
    dispatch_assets = manifest["assets"]
    for key, asset in dispatch_assets.items():
        assets.append(asset)

    lattice = manifest["lattice"]
    lattice_assets = lattice["assets"]
    for key, asset in lattice_assets.items():
        assets.append(asset)

    # Node assets
    tg = lattice["transport_graph"]

    nodes = tg["nodes"]
    for node in nodes:
        node_assets = node["assets"]
        for key, asset in node_assets.items():
            assets.append(asset)
    return assets
