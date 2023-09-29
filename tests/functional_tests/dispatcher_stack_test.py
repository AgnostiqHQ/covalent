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
Integration test for the dispatcher.
"""

import pytest

import covalent_dispatcher as dispatcher
from covalent._results_manager import results_manager as rm
from covalent._shared_files.defaults import parameter_prefix

from .data import get_mock_result, get_mock_result_2, get_mock_result_3


@pytest.mark.parametrize(
    "mock_result,expected_res, expected_node_outputs",
    [
        (get_mock_result, 1, {"identity": 1, f"{parameter_prefix}1": 1}),
        (
            get_mock_result_2,
            1,
            {
                "product": 1,
                f"{parameter_prefix}1": 1,
                f"{parameter_prefix}1": 1,
                "identity": 1,
            },
        ),
        (
            get_mock_result_3,
            1,
            {"pipeline": 1, f"{parameter_prefix}1": 1, f"{parameter_prefix}1": 1},
        ),
    ],
)
def test_dispatcher_flow(mock_result, expected_res, expected_node_outputs):
    """Integration test that given a results object, plans and executes the workflow on the
    default executor.
    """

    import asyncio

    mock_result_object = mock_result()
    serialized_lattice = mock_result_object.lattice.serialize_to_json()

    awaitable = dispatcher.run_dispatcher(json_lattice=serialized_lattice)
    dispatch_id = asyncio.run(awaitable)
    rm._delete_result(dispatch_id=dispatch_id, remove_parent_directory=True)
