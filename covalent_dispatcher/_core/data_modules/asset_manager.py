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

"""
Utilties to transfer data between Covalent and compute backends
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

from covalent._shared_files import logger
from covalent._shared_files.schemas.asset import AssetUpdate

from ..._dal.result import get_result_object as get_result_object

app_log = logger.app_log
am_pool = ThreadPoolExecutor()


# Consumed by Runner
async def upload_asset_for_nodes(dispatch_id: str, key: str, dest_uris: dict):
    """Typical keys: "output", "deps", "call_before", "call_after", "function"""

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        am_pool,
        upload_asset_for_nodes_sync,
        dispatch_id,
        key,
        dest_uris,
    )


def upload_asset_for_nodes_sync(dispatch_id: str, key: str, dest_uris: dict):
    result_object = get_result_object(dispatch_id, bare=True)
    tg = result_object.lattice.transport_graph

    uploads_by_node = {}

    with result_object.session() as session:
        for node_id, dest_uri in dest_uris.items():
            if dest_uri:
                node = tg.get_node(node_id, session)
                asset = node.get_asset(key, session)
                uploads_by_node[node_id] = (asset, dest_uri)

    for _, pending_upload in uploads_by_node.items():
        asset, dest_uri = pending_upload
        asset.upload(dest_uri)


async def download_assets_for_node(
    dispatch_id: str, node_id: int, asset_updates: Dict[str, AssetUpdate]
):
    # Keys for src_uris: "output", "stdout", "stderr"

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        am_pool,
        download_assets_for_node_sync,
        dispatch_id,
        node_id,
        asset_updates,
    )


def download_assets_for_node_sync(
    dispatch_id: str, node_id: int, asset_updates: Dict[str, AssetUpdate]
):
    result_object = get_result_object(dispatch_id, bare=True)
    tg = result_object.lattice.transport_graph
    node = tg.get_node(node_id)

    db_updates = {}

    # Mapping from asset key to (Asset, remote uri)
    assets_to_download = {}

    # Prepare asset metadata update; prune empty fields
    with result_object.session() as session:
        for key in asset_updates:
            asset_update = asset_updates[key]
            if asset_update.remote_uri:
                asset = node.get_asset(key, session)
                assets_to_download[key] = (asset, asset_update.remote_uri)
            # Prune unset fields
            db_updates[key] = {attr: val for attr, val in asset_update if val is not None}

        node.update_assets(db_updates, session)

    for key, pending_download in assets_to_download.items():
        asset, remote_uri = pending_download
        asset.download(remote_uri)
