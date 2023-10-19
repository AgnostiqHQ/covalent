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

"""Logs functional test"""


import pytest

from covalent_ui.api.v1.data_layer.logs_dal import Logs
from covalent_ui.api.v1.utils.log_handler import log_config

from ..utils.assert_data.logs import seed_logs_data
from ..utils.trigger_events import shutdown_event, startup_event

output_data = seed_logs_data()
UI_LOGFILE = "covalent_ui.api.v1.data_layer.logs_dal.UI_LOGFILE"


@pytest.fixture(scope="module", autouse=True)
def env_setup():
    startup_event()
    yield
    shutdown_event()


def test_download_logs(mocker):
    """Test Download Logs"""
    logs = Logs()
    test_data = output_data["test_download_logs"]["case_functional_1"]
    mocker.patch(
        UI_LOGFILE,
        "tests/covalent_ui_backend_tests/utils/mock_files/log_files/case_3.log",
    )
    response = logs.download_logs()
    if test_data["response_type"]:
        assert type(response).__name__ == test_data["response_type"]


def test_log_handler():
    """Test Log Handler config data"""
    test_data = output_data["test_logs_handler"]["handler_format1"]
    config = log_config()
    assert config == test_data


def test_log_handler_without_level(mocker):
    """Test Log Handler config data (without level information)"""
    mocker.patch("covalent_ui.api.v1.utils.log_handler.log_to_file", False)
    test_data = output_data["test_logs_handler"]["handler_format2"]
    config = log_config()
    assert config == test_data
