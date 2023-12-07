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

"""Functions to convert lattice -> LatticeSchema"""

from typing import List

from .._results_manager.result import Result
from .._shared_files.schemas.result import (
    ASSET_FILENAME_MAP,
    AssetSchema,
    ResultAssets,
    ResultMetadata,
    ResultSchema,
)
from .._shared_files.util_classes import Status
from .common import AssetType, load_asset, save_asset
from .lattice import deserialize_lattice, serialize_lattice

__all__ = [
    "serialize_result",
    "deserialize_result",
    "strip_local_uris",
    "merge_response_manifest",
    "extract_assets",
]


ASSET_TYPES = {
    "error": AssetType.TEXT,
    "result": AssetType.TRANSPORTABLE,
}


def _serialize_result_metadata(res: Result) -> ResultMetadata:
    return ResultMetadata(
        dispatch_id=res._dispatch_id,
        root_dispatch_id=res._root_dispatch_id,
        status=str(res._status),
        start_time=res._start_time,
        end_time=res._end_time,
    )


def _deserialize_result_metadata(meta: ResultMetadata) -> dict:
    return {
        "_dispatch_id": meta.dispatch_id,
        "_root_dispatch_id": meta.root_dispatch_id,
        "_status": Status(meta.status),
        "_start_time": meta.start_time,
        "_end_time": meta.end_time,
    }


def _serialize_result_assets(res: Result, storage_path: str) -> ResultAssets:
    # NOTE: We can avoid pickling here since the UI actually consumes only the string representation

    error_asset = save_asset(
        res._error, ASSET_TYPES["error"], storage_path, ASSET_FILENAME_MAP["error"]
    )
    result_asset = save_asset(
        res._result,
        ASSET_TYPES["result"],
        storage_path,
        ASSET_FILENAME_MAP["result"],
    )
    return ResultAssets(result=result_asset, error=error_asset)


def _deserialize_result_assets(assets: ResultAssets) -> dict:
    error = load_asset(assets.error, ASSET_TYPES["error"])
    result = load_asset(assets.result, ASSET_TYPES["result"])
    return {"_result": result, "_error": error}


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
    manifest = res.model_copy(deep=True).model_dump()

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

    return ResultSchema.model_validate(manifest)


# Functions to postprocess response from dispatcher


def merge_response_manifest(manifest: ResultSchema, response: ResultSchema) -> ResultSchema:
    """Merge the dispatcher's response with the submitted manifest.

    Args:
        manifest: The manifest submitted to the `/register` endpoint.
        response: The manifest returned from `/register`.
    Returns:
        A combined manifest with asset `remote_uri`s populated.
    """

    manifest.metadata.dispatch_id = response.metadata.dispatch_id
    manifest.metadata.root_dispatch_id = response.metadata.root_dispatch_id

    # Workflow asset uris
    dispatch_assets = response.assets
    for key, asset in manifest.assets:
        remote_asset = getattr(dispatch_assets, key)
        asset.remote_uri = remote_asset.remote_uri

    lattice = response.lattice
    lattice_assets = lattice.assets
    for key, asset in manifest.lattice.assets:
        remote_asset = getattr(lattice_assets, key)
        asset.remote_uri = remote_asset.remote_uri

    # Node asset uris
    tg = lattice.transport_graph

    # Sort returned nodes b/c task packing may reorder nodes
    tg.nodes.sort(key=lambda x: x.id)
    nodes = manifest.lattice.transport_graph.nodes

    for i, node in enumerate(nodes):
        returned_node = tg.nodes[i]
        returned_node_assets = returned_node.assets
        for key, asset in node.assets:
            remote_asset = getattr(returned_node_assets, key)
            asset.remote_uri = remote_asset.remote_uri
    return manifest


def extract_assets(manifest: ResultSchema) -> List[AssetSchema]:
    """
    Extract all of the asset metadata from a manifest dictionary.

    Args:
        manifest: A result manifest

    Returns:
        A list of assets

    """

    # workflow-level assets
    dispatch_assets = manifest.assets
    assets = [asset for key, asset in dispatch_assets]
    lattice = manifest.lattice
    lattice_assets = lattice.assets
    assets.extend(asset for key, asset in lattice_assets)

    # Node assets
    tg = lattice.transport_graph
    nodes = tg.nodes
    for node in nodes:
        node_assets = node.assets
        assets.extend(asset for key, asset in node_assets)
    return assets
