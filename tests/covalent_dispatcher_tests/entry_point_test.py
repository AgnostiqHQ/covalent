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

"""Unit tests for the FastAPI app."""


import pytest

from covalent_dispatcher.entry_point import cancel_running_dispatch, run_dispatcher

DISPATCH_ID = "f34671d1-48f2-41ce-89d9-9a8cb5c60e5d"


class MockObject:
    pass


def mock_initialize_result_object(lattice):
    result = MockObject()
    result.dispatch_id = lattice["dispatch_id"]
    return result


@pytest.mark.asyncio
async def test_run_dispatcher(mocker):
    mocker.patch(
        "covalent_dispatcher._core.initialize_result_object", mock_initialize_result_object
    )
    mock_run_workflow = mocker.patch("covalent_dispatcher._core.run_workflow")
    dispatch_id = await run_dispatcher({"dispatch_id": DISPATCH_ID})
    assert dispatch_id == DISPATCH_ID
    mock_run_workflow.assert_called_once()


def test_cancel_running_dispatch(mocker):
    mock_cancel_workflow = mocker.patch("covalent_dispatcher._core.cancel_workflow")
    cancel_running_dispatch(DISPATCH_ID)
    mock_cancel_workflow.assert_called_once_with(DISPATCH_ID)
