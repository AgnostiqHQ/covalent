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

"""Main Test"""

import os
from pathlib import Path

import pytest
from fastapi.templating import Jinja2Templates

from .. import fastapi_app
from ..utils.assert_data.main import main_mock_data
from ..utils.client_template import MethodType, TestClientTemplate
from ..utils.trigger_events import shutdown_event, startup_event

object_test_template = TestClientTemplate()
output_data = main_mock_data()


@pytest.fixture(scope="module", autouse=True)
def env_setup():
    startup_event()
    yield
    shutdown_event()


def test_webhook():
    """Test webhook"""
    test_data = output_data["test_webhook"]["case1"]
    response = object_test_template(
        api_path=output_data["test_webhook"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data={},
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_draw(mocker):
    """Test Draw API"""
    test_data = output_data["test_draw"]["case1"]
    response = object_test_template(
        api_path=output_data["test_draw"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data={},
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_root(mocker):
    """Test root API"""
    path = str(Path(__file__).parent.parent.parent.parent.absolute()) + "/covalent_ui/webapp/build"
    if os.path.exists(path):
        mocker.patch("covalent_ui.app.templates", Jinja2Templates(directory=path))
        test_data = output_data["test_misc"]["case1"]
        response = object_test_template(
            api_path=output_data["test_misc"]["api_path"],
            app=fastapi_app,
            method_type=MethodType.GET,
            path=test_data["path"],
        )
        assert response.status_code == test_data["status_code"]
