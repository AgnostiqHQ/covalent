# Copyright 2023 Agnostiq Inc.
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
Tests for the querying and updating dispatches
"""


from unittest.mock import MagicMock

import pytest

from covalent_dispatcher._core.data_modules import dispatch


@pytest.mark.asyncio
async def test_get(mocker):
    dispatch_id = "test_get_incoming_edges"

    mock_retval = MagicMock()
    mock_result_obj = MagicMock()
    mock_result_obj.get_values = MagicMock(return_value=mock_retval)
    mocker.patch(
        "covalent_dispatcher._core.data_modules.dispatch.get_result_object",
        return_value=mock_result_obj,
    )

    assert mock_retval == await dispatch.get(dispatch_id, keys=["status"])


@pytest.mark.asyncio
async def test_get_incomplete_tasks(mocker):
    dispatch_id = "test_get_node_successors"
    mock_retval = MagicMock()
    mock_result_obj = MagicMock()
    mock_result_obj._get_incomplete_nodes = MagicMock(return_value=mock_retval)
    mocker.patch(
        "covalent_dispatcher._core.data_modules.dispatch.get_result_object",
        return_value=mock_result_obj,
    )

    assert mock_retval == await dispatch.get_incomplete_tasks(dispatch_id)


@pytest.mark.asyncio
async def test_update(mocker):
    dispatch_id = "test_update_dispatch"
    mock_result_obj = MagicMock()
    mocker.patch(
        "covalent_dispatcher._core.data_modules.dispatch.get_result_object",
        return_value=mock_result_obj,
    )

    await dispatch.update(dispatch_id, {"status": "COMPLETED"})

    mock_result_obj._update_dispatch.assert_called()
