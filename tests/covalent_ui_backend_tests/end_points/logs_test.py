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
"""Logs Test"""

import pytest

from .. import fastapi_app
from ..utils.assert_data.logs import seed_logs_data
from ..utils.client_template import MethodType, TestClientTemplate
from ..utils.trigger_events import shutdown_event, startup_event

object_test_template = TestClientTemplate()
output_data = seed_logs_data()

UI_LOGFILE = "covalent_ui.api.v1.data_layer.logs_dal.UI_LOGFILE"


@pytest.fixture(scope="module", autouse=True)
def env_setup():
    startup_event()
    yield
    shutdown_event()


def __get_custom_response(case: str):
    """Get custom response for logs test case"""
    test_data = output_data["test_logs"][case]
    request = test_data["request_data"]["query"]
    response = object_test_template(
        api_path=output_data["test_logs"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
        query_data=request,
    )
    return {"response": response.json(), "request": request}


def test_logs(mocker):
    """Test Logs API"""
    mocker.patch(
        UI_LOGFILE,
        "tests/covalent_ui_backend_tests/utils/mock_files/log_files/case_1.log",
    )
    test_data = output_data["test_logs"]["case1"]
    response = object_test_template(
        api_path=output_data["test_logs"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_logs_case2(mocker):
    """Test Logs API"""
    mocker.patch(
        UI_LOGFILE,
        "tests/covalent_ui_backend_tests/utils/mock_files/log_files/case_3.log",
    )
    test_data = output_data["test_logs"]["case1_1"]
    response = object_test_template(
        api_path=output_data["test_logs"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_logs_with_queries(mocker):
    """Test Logs With Queries"""
    mocker.patch(
        UI_LOGFILE,
        "tests/covalent_ui_backend_tests/utils/mock_files/log_files/case_2.log",
    )
    test_cases = ["case2", "case3", "case4"]
    json_data = [__get_custom_response(case) for case in test_cases]

    # Case 2 Scenario
    assert (
        len(json_data[0]["response"]["items"]) == json_data[0]["request"]["count"]
        and json_data[0]["response"]["total_count"] == 7
    )

    # Case 3 Scenario
    assert len(json_data[1]["response"]["items"]) == (
        json_data[1]["response"]["total_count"] - json_data[1]["request"]["offset"]
    )

    # Case 4 Scenario
    assert len(json_data[2]["response"]["items"]) == 1


def test_non_existing_logs(mocker):
    """Test Logs with missing file / data"""
    mocker.patch(
        UI_LOGFILE,
        "tests/covalent_ui_backend_tests/utils/mock_files/log_files/case_4.log",
    )
    test_data = output_data["test_logs"]["case5"]
    response = object_test_template(
        api_path=output_data["test_logs"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_download_log(mocker):
    """Test download logs"""
    mocker.patch(
        UI_LOGFILE,
        "tests/covalent_ui_backend_tests/utils/mock_files/log_files/case_b.log",
    )
    test_data = output_data["test_download_logs"]["case1"]
    response = object_test_template(
        api_path=output_data["test_download_logs"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
    )
    assert response.status_code == test_data["status_code"]
    assert isinstance(response.content, bytes)
