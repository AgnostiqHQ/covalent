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

import uuid
from concurrent.futures import ThreadPoolExecutor

from covalent._results_manager.result import Result
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._workflow.transport import _TransportGraph

app_log = logger.app_log
log_stack_info = logger.log_stack_info

futures = {}


def get_unique_id() -> str:
    """
    Get a unique ID.

    Args:
        None

    Returns:
        str: Unique ID
    """

    return str(uuid.uuid4())


def run_dispatcher(
    json_lattice: str, workflow_pool: ThreadPoolExecutor, tasks_pool: ThreadPoolExecutor
) -> str:
    """
    Run the dispatcher from the lattice asynchronously using Dask.
    Assign a new dispatch id to the result object and return it.
    Also save the result in this initial stage to the file mentioned in the result object.

    Args:
        json_lattice: A JSON-serialized lattice

    Returns:
        dispatch_id: A string containing the dispatch id of current dispatch.
    """

    dispatch_id = get_unique_id()
    from covalent._workflow.lattice import Lattice
    from covalent_dispatcher._db.dispatchdb import DispatchDB

    from ._core import run_workflow

    lattice = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lattice, lattice.metadata["results_dir"])
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    app_log.debug("2: Constructed result object and initialized nodes.")
    result_object.persist()

    app_log.debug("Result object retrieved.")

    futures[dispatch_id] = workflow_pool.submit(run_workflow, result_object, tasks_pool)
    app_log.debug("Submitted lattice JSON to run_workflow.")

    return dispatch_id


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
