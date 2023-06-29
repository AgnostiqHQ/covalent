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
Tests for the cancellation module
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from covalent._shared_files.util_classes import RESULT_STATUS
from covalent_dispatcher._core.runner_modules import cancel


@pytest.mark.asyncio
async def test_cancel_tasks(mocker):
    """Test the public `cancel_tasks` function"""
    dispatch_id = "test_cancel_tasks"
    node_id = 0
    mock_node_metadata = [{"executor": "dask", "executor_data": {}}]
    mock_job_metadata = [{"job_handle": 42}]
    mock_cancel_priv = mocker.patch("covalent_dispatcher._core.runner_modules.cancel._cancel_task")

    mocker.patch(
        "covalent_dispatcher._core.runner_modules.cancel._get_metadata_for_nodes",
        return_value=mock_node_metadata,
    )
    mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.get_jobs_metadata",
        return_value=mock_job_metadata,
    )

    await cancel.cancel_tasks(dispatch_id, [node_id])

    assert mock_cancel_priv.call_count == 1


@pytest.mark.asyncio
async def test_cancel_task_priv(mocker):
    """Test the internal `_cancel_task` function"""
    mock_executor = MagicMock()
    mock_executor._cancel = AsyncMock(return_value=True)
    mock_set_status = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.set_job_status"
    )

    mocker.patch(
        "covalent_dispatcher._core.runner_modules.cancel.get_executor", return_value=mock_executor
    )

    dispatch_id = "test_cancel_task_priv"
    job_handle = json.dumps(42)
    task_id = 0

    await cancel._cancel_task(dispatch_id, task_id, ["dask", {}], job_handle)

    task_meta = {"dispatch_id": dispatch_id, "node_id": task_id}

    mock_executor._cancel.assert_awaited_with(task_meta, 42)

    mock_set_status.assert_awaited_with(dispatch_id, task_id, str(RESULT_STATUS.CANCELLED))


@pytest.mark.asyncio
async def test_cancel_task_priv_exception(mocker):
    """Test the internal `_cancel_task` function"""
    mock_executor = MagicMock()
    mock_executor._cancel = AsyncMock(side_effect=RuntimeError())
    mock_set_status = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.set_job_status"
    )

    mocker.patch(
        "covalent_dispatcher._core.runner_modules.cancel.get_executor", return_value=mock_executor
    )

    dispatch_id = "test_cancel_task_priv"
    job_handle = json.dumps(42)
    task_id = 0

    await cancel._cancel_task(dispatch_id, task_id, ["dask", {}], job_handle)

    task_meta = {"dispatch_id": dispatch_id, "node_id": task_id}

    mock_executor._cancel.assert_awaited_with(task_meta, 42)

    mock_set_status.assert_not_awaited()
