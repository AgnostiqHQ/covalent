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
Functionality for importing dispatch submissions
"""

import asyncio
import uuid
from typing import Optional

from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.schemas.result import ResultSchema
from covalent_dispatcher._dal.importers.result import handle_redispatch, import_result
from covalent_dispatcher._dal.result import Result as SRVResult

from .utils import run_in_executor

BASE_PATH = get_config("dispatcher.results_dir")

app_log = logger.app_log


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


async def _pull_assets(manifest: ResultSchema) -> None:
    dispatch_id = manifest.metadata.dispatch_id
    assets = await run_in_executor(_get_all_assets, dispatch_id)
    futs = []
    for asset in assets["lattice"]:
        if asset.remote_uri:
            futs.append(run_in_executor(asset.download, asset.remote_uri))

    for asset in assets["nodes"]:
        if asset.remote_uri:
            futs.append(run_in_executor(asset.download, asset.remote_uri))

    await asyncio.gather(*futs)

    app_log.debug(f"imported {len(futs)} assets for dispatch {dispatch_id}")


async def import_manifest(
    manifest: ResultSchema,
    parent_dispatch_id: Optional[str],
    parent_electron_id: Optional[int],
) -> ResultSchema:
    filtered_manifest = await run_in_executor(
        _import_manifest, manifest, parent_dispatch_id, parent_electron_id
    )
    await _pull_assets(filtered_manifest)

    return filtered_manifest


def _import_derived_manifest(
    manifest: ResultSchema,
    parent_dispatch_id: str,
    reuse_previous_results: bool,
) -> ResultSchema:
    filtered_manifest = _import_manifest(manifest)
    return handle_redispatch(filtered_manifest, parent_dispatch_id, reuse_previous_results)


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

    await _pull_assets(filtered_manifest)

    return filtered_manifest
