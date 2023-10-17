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

"""Graph test"""

import pytest

from .. import fastapi_app
from ..utils.assert_data.graph import seed_graph_data
from ..utils.client_template import MethodType, TestClientTemplate
from ..utils.trigger_events import shutdown_event, startup_event

object_test_template = TestClientTemplate()
output_data = seed_graph_data()


@pytest.fixture(scope="module", autouse=True)
def env_setup():
    startup_event()
    yield
    shutdown_event()


def test_get_graph():
    """test graph API"""
    test_data = output_data["test_graph"]["case_test_get_graph"]
    response = object_test_template(
        api_path=output_data["test_graph"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_graph_invalid_dispatch_id():
    """test graph with invalid dispatch id"""
    test_data = output_data["test_graph"]["case_test_graph_invalid_dispatch_id"]
    response = object_test_template(
        api_path=output_data["test_graph"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]
