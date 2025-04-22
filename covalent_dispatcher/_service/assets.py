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

"""Endpoints for uploading and downloading workflow assets"""

from functools import lru_cache
from typing import Union

from fastapi import APIRouter, Header, HTTPException

from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.schemas.asset import AssetSchema
from covalent_dispatcher._object_store.base import TransferDirection

from .._dal.result import get_result_object
from .._db.datastore import workflow_db
from .models import ElectronAssetKey

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()

_background_tasks = set()

LRU_CACHE_SIZE = get_config("dispatcher.asset_cache_size")


@router.get("/dispatches/{dispatch_id}/electrons/{node_id}/assets/{key}")
def get_node_asset(
    dispatch_id: str,
    node_id: int,
    key: ElectronAssetKey,
) -> AssetSchema:
    """Returns an asset for an electron.

    Args:
        dispatch_id: The dispatch's unique id.
        node_id: The id of the electron.
        key: The name of the asset
    """

    try:

        result_object = get_cached_result_object(dispatch_id)

        app_log.debug(f"LRU cache info: {get_cached_result_object.cache_info()}")

        node = result_object.lattice.transport_graph.get_node(node_id)
        with workflow_db.session() as session:
            asset = node.get_asset(key=key.value, session=session)
            remote_uri = asset.object_store.get_public_uri(
                asset.storage_path, asset.object_key, direction=TransferDirection.download
            )

        return AssetSchema(size=asset.size, remote_uri=remote_uri)

    except Exception as e:
        app_log.debug(e)
        raise


@router.post("/dispatches/{dispatch_id}/electrons/{node_id}/assets/{key}")
def upload_node_asset(
    dispatch_id: str,
    node_id: int,
    key: ElectronAssetKey,
    content_length: int = Header(default=0),
    digest_alg: Union[str, None] = Header(default=None),
    digest: Union[str, None] = Header(default=None),
) -> AssetSchema:
    """Upload an electron asset.

    Args:
        dispatch_id: The dispatch's unique id.
        node_id: The electron id.
        key: The name of the asset
        asset_file: (body) The file to be uploaded
        content_length: (header)
        digest: (header)
    """
    app_log.debug(
        f"Initiating upload for {dispatch_id}:{node_id}:{key.value} ({content_length} bytes) "
    )
    try:
        metadata = {"size": content_length, "digest_alg": digest_alg, "digest": digest}
        remote_uri = _update_node_asset_metadata(
            dispatch_id,
            node_id,
            key,
            metadata,
        )
        return AssetSchema(size=content_length, remote_uri=remote_uri)
    except Exception as e:
        app_log.debug(e)
        raise


# This must only be used for static data as we don't have yet any
# intelligent invalidation logic.
@lru_cache(maxsize=LRU_CACHE_SIZE)
def get_cached_result_object(dispatch_id: str):
    try:
        with workflow_db.session() as session:
            srv_res = get_result_object(dispatch_id, bare=False, session=session)
            app_log.debug(f"Caching result {dispatch_id}")

            # Prepopulate asset maps to avoid DB lookups

            srv_res.populate_asset_map(session)
            srv_res.lattice.populate_asset_map(session)

            tg = srv_res.lattice.transport_graph
            g = tg.get_internal_graph_copy()
            for node_id in g.nodes():
                node = tg.get_node(node_id, session)
                node.populate_asset_map(session)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"The requested dispatch ID {dispatch_id} was not found.",
        )

    return srv_res


def _filter_null_metadata(metadata):
    # Filter out null updates
    return {k: v for k, v in metadata.items() if v is not None}


def _update_node_asset_metadata(dispatch_id, node_id, key, metadata) -> str:
    result_object = get_cached_result_object(dispatch_id)

    app_log.debug(f"LRU cache info: {get_cached_result_object.cache_info()}")
    node = result_object.lattice.transport_graph.get_node(node_id)
    with workflow_db.session() as session:
        asset = node.get_asset(key=key.value, session=session)
        app_log.debug(f"Asset uri {asset.internal_uri}")

        # Update asset metadata
        update = _filter_null_metadata(metadata)
        node.update_assets(updates={key: update}, session=session)
        app_log.debug(f"Updated node asset {dispatch_id}:{node_id}:{key.value}")

        object_store = asset.object_store
        remote_uri = object_store.get_public_uri(
            asset.storage_path, asset.object_key, direction=TransferDirection.upload
        )
        return remote_uri
