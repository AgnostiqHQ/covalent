# Copyright 2023 Agnostiq Inc.
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
