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


from functools import partial

import pytest

from covalent._workflow.transport import _TransportGraph
from covalent_dispatcher._core.data_modules.job_manager import JobManager


@pytest.fixture
def mock_job_manager():
    return JobManager()


def get_mock_tg():
    tg = _TransportGraph()
    tg.add_node_by_id(0, job_id=1)
    tg.add_node_by_id(1, job_id=2)
    return tg


def to_job_ids(dispatch_id, task_ids, task_job_map):
    return list(map(lambda x: task_job_map[x], task_ids))


@pytest.mark.asyncio
async def test_get_jobs_metadata(mocker):
    task_ids = [0, 1]
    task_job_map = {0: 1, 1: 2}
    mock_to_job_ids = partial(to_job_ids, task_job_map=task_job_map)
    job_ids = mock_to_job_ids("dispatch", task_ids)
    mocker.patch("covalent_dispatcher._core.data_modules.job_manager.to_job_ids", mock_to_job_ids)
    mock_get = mocker.patch("covalent_dispatcher._core.data_modules.job_manager.get_job_records")

    await JobManager.get_jobs_metadata("dispatch", task_ids)

    mock_get.assert_called_with(job_ids)


@pytest.mark.asyncio
async def test_set_cancel_requested_private(mock_job_manager, mocker):
    mock_to_job_ids = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.to_job_ids", return_value=[0, 1]
    )

    mock_set_cancel_request_private = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.JobManager._set_cancel_requested"
    )

    await mock_job_manager.set_cancel_requested("dispatch", [0, 1])

    mock_to_job_ids.assert_called_once_with("dispatch", [0, 1])
    mock_set_cancel_request_private.assert_called_once_with([0, 1])


@pytest.mark.asyncio
async def test_set_cancel_requested(mock_job_manager, mocker):
    mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.to_job_ids", return_value=[0, 1]
    )
    mock_update = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.update_job_records"
    )

    await mock_job_manager.set_cancel_requested("dispatch", [0, 1])
    expected_args = [{"job_id": job_id, "cancel_requested": True} for job_id in [0, 1]]
    mock_update.assert_called_with(expected_args)


@pytest.mark.asyncio
async def test_set_job_handle(mock_job_manager, mocker):
    task_job_map = {0: 1, 1: 2}
    mock_to_job_ids = partial(to_job_ids, task_job_map=task_job_map)
    mocker.patch("covalent_dispatcher._core.data_modules.job_manager.to_job_ids", mock_to_job_ids)

    mock_update = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.update_job_records"
    )

    await mock_job_manager.set_job_handle(dispatch_id="dispatch", task_id=0, job_handle="12356")
    mock_update.assert_called_with([{"job_id": 1, "job_handle": "12356"}])


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_requested", [True, False])
async def test_set_cancel_result(cancel_requested, mock_job_manager, mocker):
    mock_to_job_ids = partial(to_job_ids, task_job_map={0: 1, 1: 2})
    mocker.patch("covalent_dispatcher._core.data_modules.job_manager.to_job_ids", mock_to_job_ids)
    mock_update = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.update_job_records"
    )
    await mock_job_manager.set_cancel_result("dispatch", 0, cancel_status=cancel_requested)
    mock_update.assert_called_with([{"job_id": 1, "cancel_successful": cancel_requested}])
