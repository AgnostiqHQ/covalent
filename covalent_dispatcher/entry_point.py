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

import sys
import threading
import uuid
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import List

from covalent._results_manager import Result
from covalent._results_manager import results_manager as rm
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._workflow.transport import _TransportGraph

from ._db.dispatchdb import DispatchDB

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
    from ._core import run_workflow

    futures[dispatch_id] = workflow_pool.submit(
        run_workflow, dispatch_id, json_lattice, tasks_pool
    )
    app_log.warning("0: Submitted lattice JSON to run_workflow.")

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
