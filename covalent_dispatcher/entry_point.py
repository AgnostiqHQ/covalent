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


from covalent._shared_files import logger

app_log = logger.app_log
log_stack_info = logger.log_stack_info


SLEEP = 5


async def run_dispatcher(
    json_lattice: str, disable_run: bool = False, pending_dispatch_id: str = None
):
    """
    Run the dispatcher from the lattice asynchronously using Dask.
    Assign a new dispatch id to the result object and return it.
    Also save the result in this initial stage to the file mentioned in the result object.

    Args:
        json_lattice: A JSON-serialized lattice

    Returns:
        dispatch_id: A string containing the dispatch id of current dispatch.
    """

    from ._core import make_dispatch, run_dispatch

    if pending_dispatch_id:
        run_dispatch(pending_dispatch_id)
        app_log.warning("Submitted pending result object to run_workflow.")
        return pending_dispatch_id

    else:
        dispatch_id = make_dispatch(json_lattice)

        if not disable_run:
            run_dispatch(dispatch_id)
            app_log.debug("Submitted result object to run_workflow.")

        return dispatch_id


async def run_redispatch(
    dispatch_id: str, json_lattice: str, electron_updates: dict, reuse_previous_results: bool
):
    from ._core import make_derived_dispatch, run_dispatch

    redispatch_id = make_derived_dispatch(
        dispatch_id, json_lattice, electron_updates, reuse_previous_results
    )
    run_dispatch(redispatch_id)

    app_log.debug(f"Redispatching {dispatch_id} as {redispatch_id}")

    return redispatch_id


def cancel_running_dispatch(dispatch_id: str) -> None:
    """
    Cancels a running dispatch job.

    Args:
        dispatch_id: Dispatch id of the dispatch to be cancelled.

    Returns:
        None
    """

    from ._core import cancel_workflow

    cancel_workflow(dispatch_id)
