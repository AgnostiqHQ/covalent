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

"""Unit tests for the FastAPI entry points."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from covalent_dispatcher.entry_point import cancel_running_dispatch, run_dispatcher


@pytest.mark.asyncio
async def test_run_dispatcher(mocker):
    mock_result = MagicMock()
    mock_result.dispatch_id = "test_dispatch"
    mock_initialize_result = mocker.patch(
        "covalent_dispatcher.entry_point.initialize_result_object", return_value=mock_result
    )
    mock_coro_obj = AsyncMock()()
    mm = MagicMock(return_value=mock_coro_obj)
    mock_create_task = mocker.patch("asyncio.create_task")
    mock_run_workflow = mocker.patch("covalent_dispatcher.entry_point.run_workflow", mm)

    json_lattice = "json_lattice"

    await run_dispatcher(json_lattice)

    mock_initialize_result.assert_called_once_with(json_lattice)
    mock_run_workflow.assert_called_with(mock_result)
    mock_create_task.assert_called_once()

    await mock_coro_obj


@pytest.mark.asyncio
async def test_cancel_running_dispatcher(mocker):
    dispatch_id = "asdf"
    create_task_mock = mocker.patch("asyncio.create_task")
    coro_obj_mock = AsyncMock()()
    mm = MagicMock(return_value=coro_obj_mock)

    cancel_mock = mocker.patch("covalent_dispatcher._core.cancel_workflow", mm)
    await cancel_running_dispatch(dispatch_id)
    create_task_mock.assert_called_once_with(coro_obj_mock)
    cancel_mock.assert_called_once_with(dispatch_id)

    await coro_obj_mock
