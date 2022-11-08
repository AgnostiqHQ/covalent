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

"""Logs functional test"""


from covalent_ui.api.v1.data_layer.logs_dal import Logs
from covalent_ui.api.v1.utils.log_handler import log_config
from tests.covalent_ui_backend_tests.utils.assert_data.logs import seed_logs_data

output_data = seed_logs_data()


def test_download_logs():
    """Test Download Logs"""
    logs = Logs()
    test_data = output_data["test_download_logs"]["case_functional_1"]
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
