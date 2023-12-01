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
Functionality for importing dispatch submissions
"""

import shutil
import uuid
from typing import Optional, Tuple

from covalent._dispatcher_plugins.local import decode_b64_tar, untar_staging_dir
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.schemas.result import ResultSchema
from covalent_dispatcher._dal.importers.result import handle_redispatch, import_result
from covalent_dispatcher._dal.result import Result as SRVResult

from .utils import run_in_executor

BASE_PATH = get_config("dispatcher.results_dir")

app_log = logger.app_log

# Concurrent futures for copying assets during redispatch
copy_futures = {}


# Domain: result
def get_unique_id() -> str:
    """
    Get a unique ID.

    Args:
        None

    Returns:
        str: Unique ID
    """

    return str(uuid.uuid4())


def _import_manifest(
    res: ResultSchema,
    parent_dispatch_id: Optional[str],
    parent_electron_id: Optional[int],
) -> ResultSchema:
    if not res.metadata.dispatch_id:
        res.metadata.dispatch_id = get_unique_id()

    # Compute root_dispatch_id for sublattice dispatches
    if parent_dispatch_id:
        parent_result_object = SRVResult.from_dispatch_id(
            dispatch_id=parent_dispatch_id,
            bare=True,
        )
        res.metadata.root_dispatch_id = parent_result_object.root_dispatch_id
    else:
        res.metadata.root_dispatch_id = res.metadata.dispatch_id

    return import_result(res, BASE_PATH, parent_electron_id)


def _get_all_assets(dispatch_id: str):
    result_object = SRVResult.from_dispatch_id(dispatch_id, bare=True)
    return result_object.get_all_assets()


def _pull_assets(manifest: ResultSchema) -> None:
    dispatch_id = manifest.metadata.dispatch_id
    assets = _get_all_assets(dispatch_id)
    download_count = 0
    for asset in assets["lattice"]:
        if asset.remote_uri:
            download_count += 1
            asset.download(asset.remote_uri)

    for asset in assets["nodes"]:
        if asset.remote_uri:
            download_count += 1
            asset.download(asset.remote_uri)

    app_log.debug(f"imported {download_count} assets for dispatch {dispatch_id}")


async def import_manifest(
    manifest: ResultSchema,
    parent_dispatch_id: Optional[str],
    parent_electron_id: Optional[int],
) -> ResultSchema:
    filtered_manifest = await run_in_executor(
        _import_manifest, manifest, parent_dispatch_id, parent_electron_id
    )
    await run_in_executor(_pull_assets, filtered_manifest)

    return filtered_manifest


def _import_derived_manifest(
    manifest: ResultSchema,
    parent_dispatch_id: str,
    reuse_previous_results: bool,
) -> ResultSchema:
    filtered_manifest = _import_manifest(manifest, None, None)
    filtered_manifest, assets_to_copy = handle_redispatch(
        filtered_manifest, parent_dispatch_id, reuse_previous_results
    )

    return filtered_manifest


async def import_derived_manifest(
    manifest: ResultSchema,
    parent_dispatch_id: str,
    reuse_previous_results: bool,
) -> ResultSchema:
    filtered_manifest = await run_in_executor(
        _import_derived_manifest,
        manifest,
        parent_dispatch_id,
        reuse_previous_results,
    )

    await run_in_executor(_pull_assets, filtered_manifest)

    return filtered_manifest


# Import b64 tarball of a client-side staging directory
# For handling sublattice dispatches
def import_b64_staging_tarball(
    b64_buffer: str, parent_dispatch_id: str, parent_electron_id: str
) -> Tuple[str, ResultSchema]:
    tar_path = decode_b64_tar(b64_buffer)
    work_dir, manifest = untar_staging_dir(tar_path)

    app_log.debug(f"Extracted tarball to working directory {work_dir}")
    filtered_manifest = _import_manifest(
        manifest,
        parent_dispatch_id,
        parent_electron_id,
    )
    _pull_assets(filtered_manifest)

    shutil.rmtree(work_dir)
    app_log.debug(f"Cleaned up working directory {work_dir}")
    return filtered_manifest
