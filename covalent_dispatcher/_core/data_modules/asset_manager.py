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

"""
Utilties to transfer data between Covalent and compute backends
"""

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from covalent._shared_files import logger

from ..._dal.asset import Asset
from ..._dal.result import get_result_object as get_result_object
from .file_transfer import cp

app_log = logger.app_log
am_pool = ThreadPoolExecutor()


def _upload_asset(asset: Asset, dest_uri: str):
    scheme = asset.storage_type.value
    src_uri = scheme + "://" + os.path.join(asset.storage_path, asset.object_key)
    app_log.debug(f"Uploading asset from {src_uri} to {dest_uri}")
    cp(src_uri, dest_uri)


def _download_asset(asset: Asset):
    scheme = asset.storage_type.value
    dest_uri = scheme + "://" + os.path.join(asset.storage_path, asset.object_key)
    src_uri = asset.remote_uri
    app_log.debug(f"Downloading asset from {src_uri} to {dest_uri}")

    cp(src_uri, dest_uri)


# Consumed by Runner
async def upload_asset_for_nodes(dispatch_id: str, key: str, dest_uris: dict):
    """Typical keys: "output", "deps", "call_before", "call_after", "function"""

    result_object = get_result_object(dispatch_id, bare=True)
    tg = result_object.lattice.transport_graph
    loop = asyncio.get_running_loop()

    futs = []
    for node_id, dest_uri in dest_uris.items():
        node = tg.get_node(node_id)
        asset = node.get_asset(key)
        futs.append(loop.run_in_executor(am_pool, _upload_asset, asset, dest_uri))

    await asyncio.gather(*futs)


# Consumed by update_node_result_v2 ("output_uri", "stdout_uri", "stderr_uri")
async def download_assets_for_node(dispatch_id: str, node_id: int, src_uris: dict):

    # Keys for src_uris: "output", "stdout", "stderr"

    result_object = get_result_object(dispatch_id, bare=True)
    tg = result_object.lattice.transport_graph
    loop = asyncio.get_running_loop()

    node = tg.get_node(node_id)

    futs = []
    assets_to_download = [
        node.get_asset(key).set_remote(src) for key, src in src_uris.items() if src
    ]

    for asset in assets_to_download:
        futs.append(loop.run_in_executor(am_pool, _download_asset, asset))

    await asyncio.gather(*futs)
