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
    result_object: Result, workflow_pool: ThreadPoolExecutor, tasks_pool: ThreadPoolExecutor
) -> str:
    """
    Run the dispatcher from the lattice asynchronously using Dask.
    Assign a new dispatch id to the result object and return it.
    Also save the result in this initial stage to the file mentioned in the result object.

    Args:
        result_object: A Result object containing necessary information for the dispatcher
                       to execute the workflow.

    Returns:
        dispatch_id: A string containing the dispatch id of current dispatch.
    """

    if not result_object.dispatch_id:
        dispatch_id = get_unique_id()
        result_object._dispatch_id = dispatch_id

    transport_graph = _TransportGraph()
    transport_graph.deserialize(result_object.lattice.transport_graph)
    result_object._lattice.transport_graph = transport_graph

    result_object._initialize_nodes()

    result_object.save()

    from ._core import run_workflow

    futures[dispatch_id] = workflow_pool.submit(
        run_workflow, result_object.dispatch_id, result_object.results_dir, tasks_pool
    )

    return dispatch_id


def get_result(dispatch_id: str, results_dir: str, wait: bool) -> Result:
    """
    Return the results of the dispatcher.

    Args:
        dispatch_id: Dispatch id of the result to be fetched.
        results_dir: Path of the results directory.
        wait: Whether to wait for the result to be complete/fail before returning.

    Returns:
        result: Result object containing the results of the said dispatch.
    """

    return rm._get_result_from_file(dispatch_id, results_dir, wait)


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
