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

"""Unit tests for the defaults module"""

import os
from unittest import mock

import pytest


@pytest.fixture
def env_vars():
    return {
        "HOME": "test_home",
        "LOGLEVEL": "TEST_LOG_LEVEL",
        "COVALENT_LOG_TO_FILE": "test_log",
        "COVALENT_EXECUTOR_DIR": "test_exec_dir",
    }


def test_default_sdk_config(env_vars):
    """Tests that the default SDK configuration is as expected"""

    with mock.patch.dict(os.environ, env_vars, clear=True):
        from covalent._shared_files.defaults import get_default_sdk_config

        received_config = get_default_sdk_config()

        assert received_config["config_file"] == "test_home/.config/covalent/covalent.conf"
        assert received_config["log_dir"] == "test_home/.cache/covalent"
        assert received_config["log_level"] == "test_log_level"
        assert received_config["enable_logging"] == "test_log"
        assert received_config["executor_dir"] == "test_exec_dir"
        assert received_config["no_cluster"] == "false"
