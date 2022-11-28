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

import pytest

from covalent._workflow.transport import _TransportGraph
from covalent_dispatcher._core.data_modules.job_manager import (
    _get_metadata_graph,
    _job_graphs,
    get_job_metadata,
    set_cancel_requested,
    set_cancel_result,
    set_job_handle,
)


def get_mock_tg():
    tg = _TransportGraph()
    tg.add_node_by_id(0, job_id=1)
    tg.add_node_by_id(1, job_id=2)
    return tg


@pytest.mark.asyncio
async def test_get_job_metadata(mocker):
    tg = get_mock_tg()
    _job_graphs["dispatch"] = tg
    mock_get = mocker.patch("covalent_dispatcher._core.data_modules.job_manager.get_job_records")

    await get_job_metadata("dispatch", 1)
    del _job_graphs["dispatch"]

    mock_get.assert_called_with([tg.get_node_value(1, "job_id")])


@pytest.mark.asyncio
async def test_set_cancel_requested(mocker):

    tg = get_mock_tg()
    _job_graphs["dispatch"] = tg
    mock_update = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.update_job_records"
    )
    job_id_0 = tg.get_node_value(0, "job_id")
    job_id_1 = tg.get_node_value(1, "job_id")
    await set_cancel_requested("dispatch", [0, 1])
    expected_args = [
        {"job_id": job_id_0, "cancel_requested": True},
        {"job_id": job_id_1, "cancel_requested": True},
    ]
    mock_update.assert_called_with(expected_args)


@pytest.mark.asyncio
async def test_set_job_handle(mocker):
    import json

    tg = get_mock_tg()
    _job_graphs["dispatch"] = tg
    mock_update = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.update_job_records"
    )
    job_id_0 = tg.get_node_value(0, "job_id")
    slurm_job_id = 12345
    await set_job_handle("dispatch", 0, json.dumps(slurm_job_id))
    expected_args = [{"job_id": job_id_0, "job_handle": json.dumps(slurm_job_id)}]
    mock_update.assert_called_with(expected_args)


@pytest.mark.asyncio
async def test_get_metadata_graph(mocker):
    if "dispatch_1" in _job_graphs:
        del _job_graphs["dispatch_1"]

    tg = get_mock_tg()

    mock_abstract_tg = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.abstract_tg", return_value=tg
    )

    assert await _get_metadata_graph("dispatch_1") is tg
    mock_abstract_tg.assert_called_with("dispatch_1")


@pytest.mark.asyncio
async def test_set_cancel_result(mocker):
    mock_set = mocker.patch(
        "covalent_dispatcher._core.data_modules.job_manager.set_job_metadata",
    )
    await set_cancel_result("dispatch", 1, True)
    mock_set.assert_awaited_with("dispatch", 1, cancel_successful=True)
