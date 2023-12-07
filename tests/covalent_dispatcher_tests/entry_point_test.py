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


from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from covalent_dispatcher.entry_point import (
    cancel_running_dispatch,
    register_dispatch,
    register_redispatch,
    run_dispatcher,
    start_dispatch,
)

DISPATCH_ID = "f34671d1-48f2-41ce-89d9-9a8cb5c60e5d"


@pytest.mark.asyncio
async def test_run_dispatcher(mocker):
    mock_run_dispatch = mocker.patch("covalent_dispatcher._core.run_dispatch")
    mock_make_dispatch = mocker.patch(
        "covalent_dispatcher._core.make_dispatch", return_value=DISPATCH_ID
    )
    json_lattice = '{"workflow_function": "asdf"}'
    dispatch_id = await run_dispatcher(json_lattice)
    assert dispatch_id == DISPATCH_ID
    mock_make_dispatch.assert_awaited_with(json_lattice)
    mock_run_dispatch.assert_called_with(dispatch_id)


@pytest.mark.asyncio
async def test_cancel_running_dispatch(mocker):
    mock_cancel_workflow = mocker.patch("covalent_dispatcher.entry_point.cancel_dispatch")
    await cancel_running_dispatch(DISPATCH_ID)
    mock_cancel_workflow.assert_awaited_once_with(DISPATCH_ID, [])


@pytest.mark.asyncio
async def test_start_dispatch_waits(mocker):
    """Check that start_dispatch waits for any assets to be copied."""

    dispatch_id = "test_start_dispatch_waits"

    def mock_copy():
        import time

        time.sleep(3)

    mock_futures = {}
    ex = ThreadPoolExecutor(max_workers=1)
    mocker.patch("covalent_dispatcher._core.copy_futures", mock_futures)

    mock_run_dispatch = mocker.patch("covalent_dispatcher._core.run_dispatch")

    fut = ex.submit(mock_copy)
    mock_futures[dispatch_id] = fut
    fut.add_done_callback(lambda x: mock_futures.pop(dispatch_id))

    start_time = datetime.now()
    await start_dispatch(dispatch_id)
    end_time = datetime.now()

    assert (end_time - start_time).total_seconds() > 2

    mock_run_dispatch.assert_called()


@pytest.mark.asyncio
async def test_register_dispatch(mocker):
    """Check register_dispatch"""

    mock_manifest = MagicMock()

    mock_importer = mocker.patch(
        "covalent_dispatcher._core.data_modules.importer.import_manifest",
        return_value=mock_manifest,
    )

    assert await register_dispatch("manifest", "parent_dispatch_id") is mock_manifest
    mock_importer.assert_awaited_with("manifest", "parent_dispatch_id", None)


@pytest.mark.asyncio
async def test_register_redispatch(mocker):
    """Check register_dispatch"""

    mock_manifest = MagicMock()

    mock_importer = mocker.patch(
        "covalent_dispatcher._core.data_modules.importer.import_derived_manifest",
        return_value=mock_manifest,
    )

    assert await register_redispatch("manifest", "parent_dispatch_id", True) is mock_manifest
    mock_importer.assert_awaited_with("manifest", "parent_dispatch_id", True)
