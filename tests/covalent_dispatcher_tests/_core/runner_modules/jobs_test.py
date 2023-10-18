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
Tests for the executor proxy handlers to get/set job info
"""

from unittest.mock import MagicMock

import pytest

from covalent._shared_files.util_classes import RESULT_STATUS
from covalent_dispatcher._core.runner_modules import jobs


@pytest.mark.asyncio
async def test_get_cancel_requested(mocker):
    dispatch_id = "test_get_cancel_requested"
    mock_job_records = [{"cancel_requested": True}]

    mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.get_jobs_metadata",
        return_value=mock_job_records,
    )

    assert await jobs.get_cancel_requested(dispatch_id, 0) is True


@pytest.mark.asyncio
async def test_get_version_info(mocker):
    dispatch_id = "test_get_version_info"
    mock_ver_info = {"python_version": "3.10", "covalent_version": "0.220"}

    mocker.patch(
        "covalent_dispatcher._core.runner_modules.jobs.lattice_query_module.get",
        return_value=mock_ver_info,
    )
    assert await jobs.get_version_info(dispatch_id, 0) == {"python": "3.10", "covalent": "0.220"}


@pytest.mark.asyncio
async def test_get_job_status(mocker):
    dispatch_id = "test_job_status"
    mock_job_records = [{"status": str(RESULT_STATUS.RUNNING)}]

    mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.get_jobs_metadata",
        return_value=mock_job_records,
    )

    assert await jobs.get_job_status(dispatch_id, 0) == RESULT_STATUS.RUNNING


@pytest.mark.asyncio
async def test_put_job_handle(mocker):
    dispatch_id = "test_put_job_handle"
    task_id = 0
    job_handle = "jobArn"

    mock_set = mocker.patch("covalent_dispatcher._core.data_modules.job_manager.set_job_handle")

    assert await jobs.put_job_handle(dispatch_id, task_id, job_handle) is True
    mock_set.assert_awaited_with(dispatch_id, task_id, job_handle)


@pytest.mark.asyncio
async def test_put_job_status(mocker):
    dispatch_id = "test_put_job_handle"
    task_id = 0
    status = RESULT_STATUS.RUNNING

    mock_exec_attrs = {"executor": "dask", "executor_data": {}}
    executor = MagicMock()
    executor.validate_status = MagicMock(return_value=True)

    mocker.patch(
        "covalent_dispatcher._core.data_modules.electron.get", return_value=mock_exec_attrs
    )

    mocker.patch(
        "covalent_dispatcher._core.runner_modules.jobs.get_executor", return_value=executor
    )
    mock_set = mocker.patch("covalent_dispatcher._core.data_modules.job_manager.set_job_status")

    assert await jobs.put_job_status(dispatch_id, task_id, status) is True
    mock_set.assert_awaited_with(dispatch_id, task_id, str(status))
