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
Tests for self-contained entry point for the dispatcher
"""

from concurrent.futures import ThreadPoolExecutor

import covalent
import covalent_dispatcher as dispatcher
from covalent._results_manager import results_manager as rm
from covalent_dispatcher._db.dispatchdb import DispatchDB
from tests.functional_tests.basic_dispatcher_test import workflow

from .data import TEST_RESULTS_DIR, get_mock_result


def test_run_dispatcher():
    """
    Test run_dispatcher by passing a result object for a lattice and check if no exception is raised.
    """

    workflow_pool = ThreadPoolExecutor()
    task_pool = ThreadPoolExecutor()

    try:
        dispatch_id = dispatcher.run_dispatcher(
            json_lattice=get_mock_result().lattice.serialize_to_json(),
            workflow_pool=workflow_pool,
            tasks_pool=task_pool,
        )
    except Exception as e:
        assert False, f"Exception raised: {e}"

    rm._delete_result(dispatch_id=dispatch_id, results_dir=TEST_RESULTS_DIR)
    with DispatchDB() as db:
        db.delete([dispatch_id])
    workflow_pool.shutdown()
    task_pool.shutdown()


def test_get_result():
    """
    Integration test combining run_dispatcher and get_result to ensure that a results object is
    returned once the workflow has executed.
    """
    workflow_pool = ThreadPoolExecutor()
    task_pool = ThreadPoolExecutor()

    dispatch_id = dispatcher.run_dispatcher(
        json_lattice=get_mock_result().lattice.serialize_to_json(),
        workflow_pool=workflow_pool,
        tasks_pool=task_pool,
    )
    result = dispatcher.get_result(
        results_dir=TEST_RESULTS_DIR, wait=True, dispatch_id=dispatch_id
    )
    assert isinstance(result, covalent._results_manager.result.Result)

    rm._delete_result(
        dispatch_id=dispatch_id, results_dir=TEST_RESULTS_DIR, remove_parent_directory=True
    )
    with DispatchDB() as db:
        db.delete([dispatch_id])

    workflow_pool.shutdown()
    task_pool.shutdown()
