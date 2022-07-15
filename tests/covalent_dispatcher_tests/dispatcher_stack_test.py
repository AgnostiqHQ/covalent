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
Integration test for the dispatcher.
"""

from concurrent.futures import ThreadPoolExecutor

import pytest

import covalent_dispatcher as dispatcher
from covalent._results_manager import results_manager as rm
from covalent._shared_files.defaults import parameter_prefix
from covalent_dispatcher._db.dispatchdb import DispatchDB

from .data import TEST_RESULTS_DIR, get_mock_result, get_mock_result_2, get_mock_result_3


@pytest.mark.parametrize(
    "mock_result,expected_res, expected_node_outputs",
    [
        (get_mock_result, 1, {"identity(0)": 1, f"{parameter_prefix}1(1)": 1}),
        (
            get_mock_result_2,
            1,
            {
                "product(0)": 1,
                f"{parameter_prefix}1(1)": 1,
                f"{parameter_prefix}1(2)": 1,
                "identity(3)": 1,
            },
        ),
        (
            get_mock_result_3,
            1,
            {"pipeline(0)": 1, f"{parameter_prefix}1(1)": 1, f"{parameter_prefix}1(2)": 1},
        ),
    ],
)
def test_dispatcher_flow(mock_result, expected_res, expected_node_outputs):
    """Integration test that given a results object, plans and executes the workflow on the
    default local executor.
    """

    workflow_pool = ThreadPoolExecutor()
    task_pool = ThreadPoolExecutor()

    mock_result_object = mock_result()
    serialized_lattice = mock_result_object.lattice.serialize_to_json()

    dispatch_id = dispatcher.run_dispatcher(
        json_lattice=serialized_lattice, workflow_pool=workflow_pool, tasks_pool=task_pool
    )
    result = dispatcher.get_result(
        results_dir=TEST_RESULTS_DIR, wait=True, dispatch_id=dispatch_id
    )
    assert result.dispatch_id == dispatch_id
    assert result.result == expected_res
    node_outputs = {k: v.get_deserialized() for k, v in result.get_all_node_outputs().items()}
    assert node_outputs == expected_node_outputs

    rm._delete_result(
        dispatch_id=dispatch_id, results_dir=TEST_RESULTS_DIR, remove_parent_directory=True
    )

    with DispatchDB() as db:
        db.delete([dispatch_id])

    workflow_pool.shutdown()
    task_pool.shutdown()
