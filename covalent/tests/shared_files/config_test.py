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

import importlib
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import toml

from covalent._shared_files.config import _ConfigManager, get_config, set_config
from covalent._shared_files.defaults import _DEFAULT_CONFIG


@pytest.mark.parametrize(
    "path_exists,update_config_called",
    [(False, False), (True, True)],
)
def test_config_manager_init_write_update_config(
    mocker, monkeypatch, path_exists, update_config_called
):
    """Test the init method for the config manager."""

    config_keys = [
        "sdk.log_dir",
        "sdk.executor_dir",
        "dispatcher.cache_dir",
        "dispatcher.results_dir",
        "dispatcher.log_dir",
        "user_interface.log_dir",
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        monkeypatch.setenv("COVALENT_CONFIG_DIR", tmp_dir)
        mocker.patch("covalent._shared_files.config._ConfigManager.ensure_config_file_exists")
        mocker.patch("covalent._shared_files.config.find_dotenv", return_value="")
        update_config_mock = mocker.patch(
            "covalent._shared_files.config._ConfigManager.update_config"
        )
        get_mock = mocker.patch(
            "covalent._shared_files.config._ConfigManager.get", side_effect=config_keys
        )
        path_mock = MagicMock()
        monkeypatch.setattr("covalent._shared_files.config.Path", path_mock)
        mocker.patch("os.path.exists", return_value=path_exists)

        _ConfigManager()

    get_mock_calls = get_mock.mock_calls
    path_mock_calls = path_mock.mock_calls

    for key in config_keys:
        assert mocker.call(key) in get_mock_calls and path_mock_calls


def test_set_config_str_key(mocker):
    """Test the set_config method when the input is a string."""

    cm_set_mock = mocker.patch("covalent._shared_files.config._config_manager.set")
    set_config("mock_section.mock_variable", "mock_value")
    cm_set_mock.assert_called_once_with("mock_section.mock_variable", "mock_value")


def test_set_config_dict_key(mocker):
    """Test the set_config method when the input is a dictionary."""

    cm_set_mock = mocker.patch("covalent._shared_files.config._config_manager.set")
    set_config({"mock_section.mock_variable": "mock_value"})
    cm_set_mock.assert_called_once_with("mock_section.mock_variable", "mock_value")


def test_get():
    """Test the get method for the config manager."""

    cm = _ConfigManager()

    assert cm.get("legacy_dispatcher.port") == cm.config_data["legacy_dispatcher"]["port"]


# def test_purge_config(mocker):
#     """Test the purge_config method for config manager."""

#     cm = _ConfigManager()
#     os_dir_mock = mocker.patch(
#         "covalent._shared_files.config.os.path.dirname", return_value="mock_dir"
#     )
#     rmtree_mock = mocker.patch("covalent._shared_files.config.shutil.rmtree")
#     cm.purge_config()
#     os_dir_mock.assert_called_once_with(cm.config_file)
#     rmtree_mock.assert_called_once_with("mock_dir", ignore_errors=True)


def test_get_config():
    """Test config retrieval function."""

    from covalent._shared_files.config import _config_manager

    # Case 1 - Empty list
    assert get_config(entries=[]) == _config_manager.config_data

    # Case 2 - List with one item
    assert (
        get_config(entries=["legacy_dispatcher.port"])
        == _config_manager.config_data["legacy_dispatcher"]["port"]
    )

    # Case 3 - String
    assert (
        get_config(entries="legacy_dispatcher.port")
        == _config_manager.config_data["legacy_dispatcher"]["port"]
    )

    # Case 4 - List with > 1 items

    test_list = ["legacy_dispatcher.host", "legacy_dispatcher.port"]

    assert get_config(entries=test_list) == {
        "legacy_dispatcher.host": _config_manager.config_data["legacy_dispatcher"]["host"],
        "legacy_dispatcher.port": _config_manager.config_data["legacy_dispatcher"]["port"],
    }


def test_log_to_file(mocker):
    def config(value):
        if value == "sdk.log_level":
            return "DEBUG"
        elif value == "sdk.enable_logging":
            return "TRUE"
        elif value == "sdk.log_dir":
            return "/tmp/covalent/tests"

    get_config_mock = mocker.patch("covalent._shared_files.config.get_config", side_effect=config)

    module_spec = importlib.util.find_spec("covalent._shared_files.logger")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)

    assert get_config_mock.call_count == 3

    shutil.rmtree("/tmp/covalent/tests")
