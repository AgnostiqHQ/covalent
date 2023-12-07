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

"""Unit tests for the FastAPI runner endpoints"""


import pytest
from fastapi.testclient import TestClient

from covalent_ui.app import fastapi_app as fast_app

DISPATCH_ID = "f34671d1-48f2-41ce-89d9-9a8cb5c60e5d"


@pytest.fixture
def app():
    yield fast_app


@pytest.fixture
def client():
    with TestClient(fast_app) as c:
        yield c


def test_update_node_asset(mocker, client):
    """
    Test update task status
    """
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")

    node_id = 0
    dispatch_id = "test_update_task_status"
    body = {"status": "COMPLETED"}

    mock_mark_task_ready = mocker.patch("covalent_dispatcher._core.runner_ng.mark_task_ready")
    resp = client.put(f"/api/v2/dispatches/{dispatch_id}/electrons/{node_id}/job", json=body)

    task_metadata = {"dispatch_id": dispatch_id, "node_id": node_id}
    mock_mark_task_ready.assert_called_with(task_metadata, body)


def test_update_node_asset_exception(mocker, client):
    """
    Test update task status
    """
    mocker.patch("covalent_dispatcher._service.app.cancel_all_with_status")
    node_id = 0
    dispatch_id = "test_update_task_status"
    body = {"status": "COMPLETED"}

    mock_mark_task_ready = mocker.patch(
        "covalent_dispatcher._core.runner_ng.mark_task_ready", side_effect=KeyError()
    )
    with pytest.raises(KeyError):
        client.put(f"/api/v2/dispatches/{dispatch_id}/electrons/{node_id}/job", json=body)
