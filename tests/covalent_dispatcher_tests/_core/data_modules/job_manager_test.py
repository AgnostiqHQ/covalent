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

"""
Tests for the job manager
"""

from functools import partial

import pytest

from covalent._workflow.transport import _TransportGraph
from covalent_dispatcher._core.data_modules.job_manager import (
    get_jobs_metadata,
    set_cancel_requested,
    set_cancel_result,
    set_job_handle,
)


def get_mock_tg():
    tg = _TransportGraph()
    tg.add_node_by_id(0, job_id=1)
    tg.add_node_by_id(1, job_id=2)
    return tg


def to_job_ids(dispatch_id, task_ids, task_job_map):
    return list(map(lambda x: task_job_map[x], task_ids))


@pytest.mark.asyncio
async def test_get_jobs_metadata(mocker):
    task_job_map = {0: 1, 1: 2}
    mock_to_job_ids = partial(to_job_ids, task_job_map=task_job_map)
    mocker.patch("covalent_dispatcher._core.data_modules.job_manager.to_job_ids", mock_to_job_ids)
    mock_get = mocker.patch("covalent_dispatcher._core.data_modules.job_manager.get_job_records")

    await get_jobs_metadata("dispatch", [1])

    mock_get.assert_called_with([task_job_map[1]])


@pytest.mark.asyncio
async def test_set_cancel_requested(mocker):

    task_job_map = {0: 1, 1: 2}
    mock_to_job_ids = partial(to_job_ids, task_job_map=task_job_map)
    mocker.patch("covalent_dispatcher._core.data_modules.job_manager.to_job_ids", mock_to_job_ids)

    mock_update = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.update_job_records"
    )
    job_id_0 = task_job_map[0]
    job_id_1 = task_job_map[1]
    await set_cancel_requested("dispatch", [0, 1])
    expected_args = [
        {"job_id": job_id_0, "cancel_requested": True},
        {"job_id": job_id_1, "cancel_requested": True},
    ]
    mock_update.assert_called_with(expected_args)


@pytest.mark.asyncio
async def test_set_job_handle(mocker):
    import json

    task_job_map = {0: 1, 1: 2}
    mock_to_job_ids = partial(to_job_ids, task_job_map=task_job_map)
    mocker.patch("covalent_dispatcher._core.data_modules.job_manager.to_job_ids", mock_to_job_ids)

    mock_update = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.update_job_records"
    )
    job_id_0 = task_job_map[0]
    slurm_job_id = 12345
    await set_job_handle("dispatch", 0, json.dumps(slurm_job_id))
    expected_args = [{"job_id": job_id_0, "job_handle": json.dumps(slurm_job_id)}]
    mock_update.assert_called_with(expected_args)


@pytest.mark.asyncio
async def test_set_cancel_result(mocker):
    mock_set = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager._set_job_metadata",
    )
    await set_cancel_result("dispatch", 1, True)
    mock_set.assert_awaited_with("dispatch", 1, cancel_successful=True)
