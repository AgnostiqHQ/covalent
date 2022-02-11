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
import tempfile
from unittest.mock import patch

import pytest
import toml

from covalent._shared_files.config import _ConfigManager, get_config, reload_config, set_config
from covalent._shared_files.defaults import _DEFAULT_CONFIG

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "test_files")


@pytest.mark.parametrize(
    "dir_env,conf_dir",
    [
        ("COVALENT_CONFIG_DIR", "covalent/covalent.conf"),
        ("XDG_CONFIG_DIR", "covalent/covalent.conf"),
        ("HOME", ".config/covalent/covalent.conf"),
    ],
)
def test_config_manager_init_directory_setting(monkeypatch, dir_env, conf_dir):
    """Test the init method for the config manager."""

    with tempfile.TemporaryDirectory() as tmp_dir:
        monkeypatch.setenv(dir_env, tmp_dir)
        cm = _ConfigManager()
        assert cm.config_file == f"{tmp_dir}/{conf_dir}"


@pytest.mark.parametrize(
    "path_exists,write_config_called,update_config_called",
    [(False, True, False), (True, False, True)],
)
def test_config_manager_init_write_update_config(
    mocker, monkeypatch, path_exists, write_config_called, update_config_called
):
    """Test the init method for the config manager."""

    config_keys = [
        "sdk.log_dir",
        "dispatcher.cache_dir",
        "dispatcher.results_dir",
        "dispatcher.log_dir",
        "user_interface.log_dir",
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        monkeypatch.setenv("COVALENT_CONFIG_DIR", tmp_dir)
        update_config_mock = mocker.patch(
            "covalent._shared_files.config._ConfigManager.update_config"
        )
        write_config_mock = mocker.patch(
            "covalent._shared_files.config._ConfigManager.write_config"
        )
        get_mock = mocker.patch(
            "covalent._shared_files.config._ConfigManager.get", side_effect=config_keys
        )
        path_mock = mocker.patch("pathlib.Path.__init__", return_value=None)

        mocker.patch("os.path.exists", return_value=path_exists)

        cm = _ConfigManager()
        assert hasattr(cm, "config_data")
        assert write_config_mock.called is write_config_called
        assert update_config_mock.called is update_config_called

    get_mock_calls = get_mock.mock_calls
    path_mock_calls = path_mock.mock_calls

    for key in config_keys:
        assert mocker.call(key) in get_mock_calls and path_mock_calls


@patch.dict(os.environ, {"COVALENT_CONFIG_DIR": CONFIG_DIR}, clear=True)
def test_read_config():
    """Test that configuration file is read properly."""

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
    """Test that updating the existing config data with the config file works."""

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
    """Test the set_config method when the input is a string."""

    cm_set_mock = mocker.patch("covalent._shared_files.config._config_manager.set")
    cm_write_config = mocker.patch("covalent._shared_files.config._config_manager.write_config")
    set_config("mock_section.mock_variable", "mock_value")
    cm_set_mock.assert_called_once_with("mock_section.mock_variable", "mock_value")
    cm_write_config.assert_called_once_with()


def test_set_config_dict_key(mocker):
    """Test the set_config method when the input is a dictionary."""

    cm_set_mock = mocker.patch("covalent._shared_files.config._config_manager.set")
    cm_write_config = mocker.patch("covalent._shared_files.config._config_manager.write_config")
    set_config({"mock_section.mock_variable": "mock_value"})
    cm_set_mock.assert_called_once_with("mock_section.mock_variable", "mock_value")
    cm_write_config.assert_called_once_with()


def test_generate_default_config(mocker):
    """Tests that the default configuration was loaded."""

    cm = _ConfigManager()
    cm_deepcopy_mock = mocker.patch("covalent._shared_files.config.copy.deepcopy", return_value={})

    cm.generate_default_config()
    cm_deepcopy_mock.assert_called_once_with(_DEFAULT_CONFIG)
    assert cm.config_data == _DEFAULT_CONFIG


def test_read_config(mocker):
    """Test the read_config method for the config manager."""

    cm = _ConfigManager()
    test_data = {"test": "test"}
    toml_load_mock = mocker.patch(
        "covalent._shared_files.config.toml.load", return_value=test_data
    )
    cm.read_config()
    toml_load_mock.assert_called_with(cm.config_file)
    assert cm.config_data == test_data


def test_get():
    """Test the get method for the config manager."""

    cm = _ConfigManager()

    assert cm.get("dispatcher.port") == cm.config_data["dispatcher"]["port"]


def test_generate_default_config():
    """Test that the default configuration was loaded."""

    cm = _ConfigManager()
    cm.generate_default_config()
    assert cm.config_data == _DEFAULT_CONFIG
    assert cm.config_data is not _DEFAULT_CONFIG


def test_reload_config(mocker):
    """Test the reload_config method."""

    cm_read_config = mocker.patch("covalent._shared_files.config._config_manager.read_config")
    reload_config()
    cm_read_config.assert_called_once_with()


def test_purge_config(mocker):
    """Test the purge_config method for config manager."""

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

    # Case 4 - List with > 1 items

    test_list = ["dispatcher.address", "dispatcher.port"]

    assert get_config(entries=test_list) == {
        "dispatcher.address": _config_manager.config_data["dispatcher"]["address"],
        "dispatcher.port": _config_manager.config_data["dispatcher"]["port"],
    }


def test_write_config(mocker):
    """Test the write_config method for config manager."""

    cm = _ConfigManager()
    toml_dump_mock = mocker.patch("covalent._shared_files.config.toml.dump")
    open_mock = mocker.patch("covalent._shared_files.config.open")
    mock_file = open_mock.return_value.__enter__.return_value
    cm.write_config()
    toml_dump_mock.assert_called_once_with(cm.config_data, mock_file)
    open_mock.assert_called_once_with(cm.config_file, "w")
