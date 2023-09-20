# Copyright 2021 Agnostiq Inc.
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

"""Unit tests for the FastAPI app."""


import pytest

from covalent_dispatcher.entry_point import cancel_running_dispatch, run_dispatcher, run_redispatch

DISPATCH_ID = "f34671d1-48f2-41ce-89d9-9a8cb5c60e5d"


class MockObject:
    pass


def mock_initialize_result_object(lattice):
    result = MockObject()
    result.dispatch_id = lattice["dispatch_id"]
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize("disable_run", [True, False])
async def test_run_dispatcher(mocker, disable_run):
    """
    Test run_dispatcher is called with the
    right arguments in different conditions
    """

    mock_run_dispatch = mocker.patch("covalent_dispatcher._core.run_dispatch")
    mock_make_dispatch = mocker.patch(
        "covalent_dispatcher._core.make_dispatch", return_value=DISPATCH_ID
    )
    json_lattice = '{"workflow_function": "asdf"}'

    dispatch_id = await run_dispatcher(json_lattice, disable_run)
    assert dispatch_id == DISPATCH_ID

    mock_make_dispatch.assert_called_with(json_lattice)
    if not disable_run:
        mock_run_dispatch.assert_called_with(dispatch_id)


@pytest.mark.asyncio
@pytest.mark.parametrize("is_pending", [True, False])
async def test_run_redispatch(mocker, is_pending):
    """
    Test the run_redispatch function is called
    with the right arguments in differnet conditions
    """

    make_derived_dispatch_mock = mocker.patch(
        "covalent_dispatcher._core.make_derived_dispatch", return_value="mock-redispatch-id"
    )
    run_dispatch_mock = mocker.patch("covalent_dispatcher._core.run_dispatch")
    redispatch_id = await run_redispatch(DISPATCH_ID, "mock-json-lattice", {}, False, is_pending)

    if not is_pending:
        make_derived_dispatch_mock.assert_called_once_with(
            DISPATCH_ID, "mock-json-lattice", {}, False
        )

    run_dispatch_mock.assert_called_once_with(redispatch_id)


@pytest.mark.asyncio
async def test_cancel_running_dispatch(mocker):
    mock_cancel_workflow = mocker.patch("covalent_dispatcher.entry_point.cancel_dispatch")
    await cancel_running_dispatch(DISPATCH_ID)
    mock_cancel_workflow.assert_awaited_once_with(DISPATCH_ID, [])
