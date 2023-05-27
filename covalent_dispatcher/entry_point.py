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
Self-contained entry point for the dispatcher
"""

from typing import List, Optional

from covalent._shared_files import logger
from covalent._shared_files.schemas.result import ResultSchema

from ._core import cancel_dispatch

app_log = logger.app_log
log_stack_info = logger.log_stack_info


async def make_dispatch(json_lattice: str):
    """
    Run the dispatcher from the lattice asynchronously using Dask.
    Assign a new dispatch id to the result object and return it.
    Also save the result in this initial stage to the file mentioned in the result object.

    Args:
        json_lattice: A JSON-serialized lattice

    Returns:
        dispatch_id: A string containing the dispatch id of current dispatch.
    """

    from ._core import make_dispatch

    dispatch_id = await make_dispatch(json_lattice)

    app_log.debug(f"Created new dispatch {dispatch_id}")

    return dispatch_id


async def make_redispatch(
    dispatch_id: str, json_lattice: str, electron_updates: dict, reuse_previous_results: bool
):
    from ._core import make_derived_dispatch, run_dispatch

    redispatch_id = await make_derived_dispatch(
        dispatch_id, json_lattice, electron_updates, reuse_previous_results
    )

    app_log.debug(f"Re-dispatching {dispatch_id} as {redispatch_id}")

    return redispatch_id


async def start_dispatch(dispatch_id: str):
    """
    Run the dispatcher from the lattice asynchronously using Dask.
    Assign a new dispatch id to the result object and return it.
    Also save the result in this initial stage to the file mentioned in the result object.

    Args:
        json_lattice: A JSON-serialized lattice

    Returns:
        dispatch_id: A string containing the dispatch id of current dispatch.
    """

    from ._core import run_dispatch

    # TODO: must be idempotent
    run_dispatch(dispatch_id)
    app_log.debug(f"Running dispatch {dispatch_id}")


async def run_dispatcher(json_lattice: str):
    """
    Run the dispatcher from the lattice asynchronously using Dask.
    Assign a new dispatch id to the result object and return it.
    Also save the result in this initial stage to the file mentioned in the result object.

    Args:
        json_lattice: A JSON-serialized lattice

    Returns:
        dispatch_id: A string containing the dispatch id of current dispatch.
    """

    dispatch_id = await make_dispatch(json_lattice)
    await start_dispatch(dispatch_id)

    app_log.debug("Submitted result object to run_workflow.")

    return dispatch_id


async def run_redispatch(
    dispatch_id: str, json_lattice: str, electron_updates: dict, reuse_previous_results: bool
):
    from ._core import make_derived_dispatch, run_dispatch

    redispatch_id = await make_redispatch(
        dispatch_id, json_lattice, electron_updates, reuse_previous_results
    )
    await start_dispatch(redispatch_id)

    app_log.debug(f"Re-dispatching {dispatch_id} as {redispatch_id}")

    return redispatch_id


async def cancel_running_dispatch(dispatch_id: str, task_ids: List[int] = None) -> None:
    """
    Cancels a running dispatch job.

    Args:
        dispatch_id: Dispatch id of the dispatch to be cancelled.

    Returns:
        None
    """

    if task_ids is None:
        task_ids = []

    await cancel_dispatch(dispatch_id, task_ids)


async def register_dispatch(
    manifest: ResultSchema, parent_dispatch_id: Optional[str]
) -> ResultSchema:
    from ._core.data_modules.importer import import_manifest

    return await import_manifest(manifest, parent_dispatch_id, None)


async def register_redispatch(
    manifest: ResultSchema,
    parent_dispatch_id: str,
    reuse_previous_results: bool,
) -> ResultSchema:
    from ._core.data_modules.importer import import_derived_manifest

    return await import_derived_manifest(
        manifest,
        parent_dispatch_id,
        reuse_previous_results,
    )
