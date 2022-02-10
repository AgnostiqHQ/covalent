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

import copy
import os
import tempfile
from asyncore import dispatcher
from functools import reduce
from operator import getitem
from unittest.mock import patch

import mock
import pytest
import toml

from covalent._shared_files.config import _ConfigManager, get_config, reload_config, set_config
from covalent._shared_files.defaults import _DEFAULT_CONFIG

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "test_files")


@pytest.mark.parametrize("dir_env", [("COVALENT_CONFIG_DIR"), ("XDG_CONFIG_DIR"), ("HOME")])
def test_config_manager_init(monkeypatch, dir_env):
    """Test the init method for the config manager."""

    with tempfile.TemporaryDirectory() as tmp_dir:
        monkeypatch.setenv(dir_env, tmp_dir)
        cm = _ConfigManager()
        assert cm.config_file == f"{tmp_dir}/covalent/covalent.conf"


@patch.dict(os.environ, {"COVALENT_CONFIG_DIR": CONFIG_DIR}, clear=True)
def test_read_config():
    """Test that configuration file is properly read"""

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


@patch.dict(os.environ, {"COVALENT_CONFIG_DIR": CONFIG_DIR}, clear=True)
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


def test_set_config_str_key(mocker):
    cm_set_mock = mocker.patch("covalent._shared_files.config._config_manager.set")
    cm_write_config = mocker.patch("covalent._shared_files.config._config_manager.write_config")
    set_config("mock_section.mock_variable", "mock_value")
    cm_set_mock.assert_called_once_with("mock_section.mock_variable", "mock_value")
    cm_write_config.assert_called_once_with()


def test_set_config_dict_key(mocker):
    cm_set_mock = mocker.patch("covalent._shared_files.config._config_manager.set")
    cm_write_config = mocker.patch("covalent._shared_files.config._config_manager.write_config")
    set_config({"mock_section.mock_variable": "mock_value"})
    cm_set_mock.assert_called_once_with("mock_section.mock_variable", "mock_value")
    cm_write_config.assert_called_once_with()


def test_generate_default_config(mocker):

    test_class = _ConfigManager()
    cm_deepcopy_mock = mocker.patch("covalent._shared_files.config.copy.deepcopy", return_value={})

    test_class.generate_default_config()
    cm_deepcopy_mock.assert_called_once_with(_DEFAULT_CONFIG)
    assert test_class.config_data == _DEFAULT_CONFIG


def test_read_config(mocker):
    cm = _ConfigManager()
    test_data = {"test": "test"}
    toml_load_mock = mocker.patch(
        "covalent._shared_files.config.toml.load", return_value=test_data
    )
    cm.read_config()
    toml_load_mock.assert_called_with(cm.config_file)
    assert cm.config_data == test_data


def test_write_config_example_1():
    """Bad example"""

    cm = _ConfigManager()
    expected_data = cm.config_data
    with tempfile.NamedTemporaryFile() as fp:
        cm.config_file = str(fp.name)
        print(f"Config file name: {cm.config_file}")
        cm.write_config()
        actual_data = toml.load(str(fp.name))

    assert expected_data == actual_data


# def test_write_config_example_2(mocker):
#     """another example"""

#     toml_mock = mocker.patch("covalent._shared_files.config.toml.dump")
#     cm = _ConfigManager()

#     with mock.patch(
#         "covalent._shared_files.config.open", mock.mock_open(read_data="1984")
#     ) as mock_file:
#         cm.update_config()
#         toml_mock.assert_called_once()


def test_get():
    test_class = _ConfigManager()

    assert test_class.get("dispatcher.port") == test_class.config_data["dispatcher"]["port"]


def test_generate_default_config():

    test_class = _ConfigManager()
    test_class.generate_default_config()
    assert test_class.config_data == _DEFAULT_CONFIG
    assert test_class.config_data is not _DEFAULT_CONFIG


def test_reload_config(mocker):

    cm_read_config = mocker.patch("covalent._shared_files.config._config_manager.read_config")
    reload_config()
    cm_read_config.assert_called_once_with()


def test_purge_config(mocker):

    cm = _ConfigManager()
    os_dir_mock = mocker.patch(
        "covalent._shared_files.config.os.path.dirname", return_value="mock_dir"
    )
    rmtree_mock = mocker.patch("covalent._shared_files.config.shutil.rmtree")
    cm.purge_config()
    os_dir_mock.assert_called_once_with(cm.config_file)
    rmtree_mock.assert_called_once_with("mock_dir", ignore_errors=True)


def test_get_config():
    """Test config retrieval function."""

    from covalent._shared_files.config import _config_manager

    # Case 1 - Empty list
    assert get_config(entries=[]) == _config_manager.config_data

    # Case 2 - List with one item
    assert (
        get_config(entries=["dispatcher.port"])
        == _config_manager.config_data["dispatcher"]["port"]
    )

    # Case 3 - String
    assert (
        get_config(entries="dispatcher.port") == _config_manager.config_data["dispatcher"]["port"]
    )

    # Case 4 - List with >1 items

    test_list = ["dispatcher.address", "dispatcher.port"]

    assert get_config(entries=test_list) == {
        "dispatcher.address": _config_manager.config_data["dispatcher"]["address"],
        "dispatcher.port": _config_manager.config_data["dispatcher"]["port"],
    }
