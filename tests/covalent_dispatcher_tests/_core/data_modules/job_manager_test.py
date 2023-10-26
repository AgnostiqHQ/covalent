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

from functools import partial

import pytest

from covalent_dispatcher._core.data_modules.job_manager import (
    get_jobs_metadata,
    set_cancel_requested,
    set_job_handle,
    set_job_status,
)


def to_job_ids(dispatch_id, task_ids, task_job_map):
    return list(map(lambda x: task_job_map[x], task_ids))


@pytest.mark.asyncio
async def test_get_jobs_metadata(mocker):
    """
    Test retrieving jobs metadata
    """
    task_ids = [0, 1]
    task_job_map = {0: 1, 1: 2}
    mock_to_job_ids = partial(to_job_ids, task_job_map=task_job_map)
    job_ids = mock_to_job_ids("dispatch", task_ids)
    mocker.patch("covalent_dispatcher._core.data_modules.job_manager.to_job_ids", mock_to_job_ids)
    mock_get = mocker.patch("covalent_dispatcher._core.data_modules.job_manager.get_job_records")

    await get_jobs_metadata("dispatch", task_ids)

    mock_get.assert_called_with(job_ids)


@pytest.mark.asyncio
async def test_set_cancel_requested_private(mocker):
    """
    Test the private get cancel requested module method
    """
    mock_to_job_ids = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.to_job_ids", return_value=[0, 1]
    )

    mock_set_cancel_request_private = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager._set_cancel_requested"
    )

    await set_cancel_requested("dispatch", [0, 1])

    mock_to_job_ids.assert_called_once_with("dispatch", [0, 1])
    mock_set_cancel_request_private.assert_called_once_with([0, 1])


@pytest.mark.asyncio
async def test_set_cancel_requested(mocker):
    """
    Test set cancel requested
    """
    mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.to_job_ids", return_value=[0, 1]
    )
    mock_update = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.update_job_records"
    )

    await set_cancel_requested("dispatch", [0, 1])
    expected_args = [{"job_id": job_id, "cancel_requested": True} for job_id in [0, 1]]
    mock_update.assert_called_with(expected_args)


@pytest.mark.asyncio
async def test_set_job_handle(mocker):
    """
    Test set job handle method
    """
    task_job_map = {0: 1, 1: 2}
    mock_to_job_ids = partial(to_job_ids, task_job_map=task_job_map)
    mocker.patch("covalent_dispatcher._core.data_modules.job_manager.to_job_ids", mock_to_job_ids)

    mock_update = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.update_job_records"
    )

    await set_job_handle(dispatch_id="dispatch", task_id=0, job_handle="12356")
    mock_update.assert_called_with([{"job_id": 1, "job_handle": "12356"}])


async def test_set_job_status(mocker):
    """
    Test requesting a task to be cancelled
    """
    mock_to_job_ids = partial(to_job_ids, task_job_map={0: 1, 1: 2})
    mocker.patch("covalent_dispatcher._core.data_modules.job_manager.to_job_ids", mock_to_job_ids)
    mock_update = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.update_job_records"
    )
    await set_job_status("dispatch", 0, status="COMPLETED")
    mock_update.assert_called_with([{"job_id": 1, "status": "COMPLEtED"}])
