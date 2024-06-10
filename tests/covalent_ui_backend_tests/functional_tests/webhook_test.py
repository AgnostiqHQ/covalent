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

"""Result webhook functional test"""


import pytest

import covalent as ct
from covalent._results_manager import Result
from covalent._shared_files.config import get_config
from covalent._workflow.lattice import Lattice
from covalent_ui.result_webhook import get_ui_url, send_draw_request, send_update

from ..utils.assert_data.sample_result_webhook import result_mock_data

pytest_plugins = ("pytest_asyncio",)
mock_data = result_mock_data()
UI_PIDFILE = get_config("dispatcher.cache_dir") + "/ui.pid"


def get_mock_simple_workflow():
    """Construct a mock simple workflow corresponding to a lattice."""

    @ct.lattice(executor="local")
    def workflow(x):
        return x

    return workflow


def get_mock_result() -> Result:
    """Construct a mock result object corresponding to a lattice."""

    workflow = get_mock_simple_workflow()
    workflow.build_graph(x="absolute")
    received_workflow = Lattice.deserialize_from_json(workflow.serialize_to_json())
    result_object = Result(received_workflow, "pipeline_workflow")

    return result_object


def test_get_ui_url():
    """Test get UI URL"""
    case1_test = mock_data["test_result_webhooks"]["case1"]
    ui_url = get_ui_url(case1_test["test_path"])
    if case1_test["response_data"]:
        assert ui_url == case1_test["response_data"]


@pytest.mark.asyncio
async def test_send_update():
    """Test send update"""
    result_object = get_mock_result()
    response = await send_update(result_object)
    print(response)
    assert response is None


def test_send_draw_request():
    """Test draw request"""
    lattice = get_mock_simple_workflow()
    lattice.build_graph(3)
    response = send_draw_request(lattice)
    assert response is None
