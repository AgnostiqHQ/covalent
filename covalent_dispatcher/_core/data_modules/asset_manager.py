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
from .utils import run_in_executor

app_log = logger.app_log
am_pool = ThreadPoolExecutor()


# Consumed by Runner
async def upload_asset_for_nodes(dispatch_id: str, key: str, dest_uris: dict):
    """Typical keys: "output", "deps", "call_before", "call_after", "function"""

    result_object = get_result_object(dispatch_id, bare=True)
    tg = result_object.lattice.transport_graph
    loop = asyncio.get_running_loop()

    futs = []
    for node_id, dest_uri in dest_uris.items():
        if dest_uri:
            node = tg.get_node(node_id)
            asset = node.get_asset(key, session=None)
            futs.append(loop.run_in_executor(am_pool, asset.upload, dest_uri))

    await asyncio.gather(*futs)


async def download_assets_for_node(
    dispatch_id: str, node_id: int, asset_updates: Dict[str, AssetUpdate]
):
    # Keys for src_uris: "output", "stdout", "stderr"

    result_object = get_result_object(dispatch_id, bare=True)
    tg = result_object.lattice.transport_graph
    node = tg.get_node(node_id)
    loop = asyncio.get_running_loop()

    futs = []
    db_updates = {}

    # Mapping from asset key to (non-empty) remote uri
    assets_to_download = {}

    # Prepare asset metadata update; prune empty fields
    for key in asset_updates:
        update = {}
        asset = asset_updates[key].dict()
        if asset["remote_uri"]:
            assets_to_download[key] = asset["remote_uri"]
        # Prune empty fields
        for attr, val in asset.items():
            if val is not None:
                update[attr] = val
        if update:
            db_updates[key] = update

    # Update metadata using the designated DB worker thread
    await run_in_executor(node.update_assets, db_updates)

    for key, remote_uri in assets_to_download.items():
        asset = node.get_asset(key, session=None)
        # Download assets concurrently.
        futs.append(loop.run_in_executor(am_pool, asset.download, remote_uri))
    await asyncio.gather(*futs)
