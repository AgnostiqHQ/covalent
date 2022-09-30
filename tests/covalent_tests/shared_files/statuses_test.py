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

import asyncio
from unittest import mock

import pytest

from covalent._shared_files.statuses import Status, status_listener


@pytest.fixture
def status():
    return Status()


def test_default_status(status: Status):
    """Test to check functions of Status are working as expected"""

    assert status.status_name == str(status)
    identifier = status.get_identifier()
    ids = identifier.split(":")

    assert status.executor_name in ids
    assert status.category_name in ids
    assert status.status_name in ids


@pytest.mark.asyncio
async def test_status_listener_case_1(mocker: mock):

    test_status = "TEST_STATUS"

    sv_mock = mocker.MagicMock()
    sv_mock.retrieve = mocker.MagicMock(return_value=None)

    result_mock = mocker.MagicMock()
    result_mock._get_node_status.return_value = test_status

    # Case 1: current_status != node_status
    result_mock._update_node.side_effect = asyncio.CancelledError

    await status_listener(result_object=result_mock, node_id=-2, status_store=sv_mock)
    sv_mock.retrieve.assert_called_once()
    result_mock._get_node_status.assert_called_once()
    result_mock._update_node.assert_called_once()


@pytest.mark.asyncio
async def test_status_listener_case_2(mocker: mock):

    sv_mock = mocker.MagicMock()
    sv_mock.retrieve = mocker.MagicMock(return_value=None)

    result_mock = mocker.MagicMock()
    result_mock._get_node_status.return_value = None
    result_mock._get_node_status.side_effect = asyncio.CancelledError

    # Case 2: current_status == node_status
    await status_listener(result_object=result_mock, node_id=-2, status_store=sv_mock)
    sv_mock.retrieve.assert_called_once()
    result_mock._get_node_status.assert_called_once()
    assert result_mock._update_node.call_count == 0


@pytest.mark.asyncio
async def test_status_listener_case_3(mocker: mock):

    test_status = "TEST_STATUS"

    sv_mock = mocker.MagicMock()
    sv_mock.retrieve = mocker.MagicMock(return_value=test_status)

    result_mock = mocker.MagicMock()
    result_mock._get_node_status.return_value = test_status

    # Case 3: type(current_status) != type(None, RunningCategory, PendingCategory)
    await status_listener(result_object=result_mock, node_id=-2, status_store=sv_mock)
    sv_mock.retrieve.assert_called_once()
    assert result_mock._get_node_status.call_count == 0
    result_mock._update_node.assert_called_once()
