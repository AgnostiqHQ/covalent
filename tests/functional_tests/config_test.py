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

import os
from unittest.mock import patch

from covalent._shared_files.config import _ConfigManager


@patch.dict(os.environ, {"COVALENT_CONFIG_DIR": "./"}, clear=True)
def test_read_config():
    """Test that configuration file is properly read"""

    assert os.environ["COVALENT_CONFIG_DIR"] == "./"
    assert os.path.exists("covalent.conf")

    config_manager = _ConfigManager()
    config_manager.read_config()

    expected_dict = {
        "sdk": {"log_dir": "./", "log_level": "warning", "enable_logging": "false"},
        "executors": {
            "local": {
                "log_stdout": "stdout.log",
                "log_stderr": "stderr.log",
                "cache_dir": "/tmp/covalent",
                "other_params": {"name": "Local Executor", "proprietary": "False"},
            },
            "local_executor": "local.py",
            "slurm_executor": "slurmp.py",
            "ssh_executor": "ssh_executor.py",
        },
        "test_dict": {
            "1": 2,
            "3": 4,
        },
    }

    assert config_manager.config_data == expected_dict


@patch.dict(os.environ, {"COVALENT_CONFIG_DIR": "functional_test_files"}, clear=True)
def test_update_config():
    """Test that updating the existing config data with the config file works"""

    config_manager = _ConfigManager()
    config_manager.config_data = {
        "sdk": {
            "test_dir": "/tmp",
            "log_dir": {
                "dir_one": "/var",
                "dir_two": "~/.log_dir",
            },
            "log_level": "debug",
            "enable_logging": "true",
        },
        "executors": {
            "local": {
                "other_params": {
                    "proprietary": "true",
                    "params_test_dict": {
                        "a": "b",
                        "c": "d",
                    },
                }
            },
            "executor_test_dict": {
                "alpha": "beta",
                "gamma": "delta",
            },
        },
        "test_dict": None,
    }
    config_manager.update_config()

    expected_dict = {
        "sdk": {
            "test_dir": "/tmp",
            "log_dir": "./",
            "log_level": "warning",
            "enable_logging": "false",
        },
        "executors": {
            "local": {
                "log_stdout": "stdout.log",
                "log_stderr": "stderr.log",
                "cache_dir": "/tmp/covalent",
                "other_params": {
                    "name": "Local Executor",
                    "proprietary": "False",
                    "params_test_dict": {
                        "a": "b",
                        "c": "d",
                    },
                },
            },
            "local_executor": "local.py",
            "slurm_executor": "slurmp.py",
            "ssh_executor": "ssh_executor.py",
            "executor_test_dict": {
                "alpha": "beta",
                "gamma": "delta",
            },
        },
        "test_dict": {
            "1": 2,
            "3": 4,
        },
    }

    assert config_manager.config_data == expected_dict
