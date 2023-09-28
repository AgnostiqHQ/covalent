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
Tests for self-contained entry point for the dispatcher
"""


import covalent_dispatcher as dispatcher

from .data import get_mock_result


def test_run_dispatcher():
    """
    Test run_dispatcher by passing a result object for a lattice and check if no exception is raised.
    """

    import asyncio

    try:
        awaitable = dispatcher.run_dispatcher(
            json_lattice=get_mock_result().lattice.serialize_to_json()
        )
        dispatch_id = asyncio.run(awaitable)
    except Exception as e:
        assert False, f"Exception raised: {e}"
