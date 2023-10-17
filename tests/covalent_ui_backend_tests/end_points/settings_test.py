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

"""Settings API"""


import pytest

from .. import fastapi_app
from ..utils.assert_data.settings import seed_settings_data
from ..utils.client_template import MethodType, TestClientTemplate
from ..utils.trigger_events import shutdown_event, startup_event

object_test_template = TestClientTemplate()
output_data = seed_settings_data()


@pytest.fixture(scope="module", autouse=True)
def env_setup():
    startup_event()
    yield
    shutdown_event()


def test_fetch_settings():
    """Test Fetch Settings"""
    test_data = output_data["test_settings"]["case1"]
    response = object_test_template(
        api_path=output_data["test_settings"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
    )
    assert response.status_code == test_data["status_code"]
    assert ("client" in response.json()) and ("server" in response.json())


def test_post_settings():
    """Test Post Settings"""
    test_data = output_data["test_settings"]["case2"]
    response = object_test_template(
        api_path=output_data["test_settings"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_post_settings_with_params():
    """Test Post Settings With Params"""
    test_data = output_data["test_settings"]["case2"]

    response = object_test_template(
        api_path=output_data["test_settings"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_body"],
        query_data=test_data["request_params"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_settings_bad_request():
    """Test settings with bad request"""
    test_data = output_data["test_settings"]["case3"]
    response = object_test_template(
        api_path=output_data["test_settings"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_body"],
    )
    assert response.status_code == test_data["status_code"]
    response_detail = response.json()["detail"][0]
    assert response_detail["msg"] == "Key should not be empty string"


def test_settings_update_field():
    """Test settings with field updation ( bad request )"""
    test_data = output_data["test_settings"]["case4"]
    response = object_test_template(
        api_path=output_data["test_settings"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_body"],
    )
    assert response.status_code == test_data["status_code"]
    response_detail = response.json()["detail"][0]
    assert response_detail["msg"] == "Field cannot be updated"
