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

import tempfile
from dataclasses import asdict

import pytest

from covalent._shared_files.config import ConfigManager, get_config, reload_config, set_config
from covalent._shared_files.defaults import DefaultConfig

DEFAULT_CONFIG = asdict(DefaultConfig())


@pytest.mark.parametrize(
    "dir_env, conf_dir",
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
        cm = ConfigManager()
        assert cm.config_file == f"{tmp_dir}/{conf_dir}"


@pytest.mark.parametrize(
    "path_exists, write_config_called, update_config_called",
    [(False, True, False), (True, False, True)],
)
def test_config_manager_init_write_update_config(
    mocker, monkeypatch, path_exists, write_config_called, update_config_called
):
    """Test the init method for the config manager."""

    config_keys = [
        "sdk.log_dir",
        "sdk.executor_dir",
        "dispatcher.cache_dir",
        "dispatcher.results_dir",
        "dispatcher.log_dir",
        "user_interface.log_dir",
        "dispatcher.db_path",
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        monkeypatch.setenv("COVALENT_CONFIG_DIR", tmp_dir)
        update_config_mock = mocker.patch(
            "covalent._shared_files.config.ConfigManager.update_config"
        )
        write_config_mock = mocker.patch(
            "covalent._shared_files.config.ConfigManager.write_config"
        )
        get_mock = mocker.patch(
            "covalent._shared_files.config.ConfigManager.get", side_effect=config_keys
        )
        path_mock = mocker.patch("covalent._shared_files.config.Path.__init__", return_value=None)
        side_effect = None if path_exists else FileNotFoundError
        open_mock = mocker.patch("covalent._shared_files.config.open", side_effect=side_effect)

        cm = ConfigManager()
        assert hasattr(cm, "config_data")
        assert write_config_mock.called is write_config_called
        assert update_config_mock.called is update_config_called

    get_mock_calls = get_mock.mock_calls
    path_mock_calls = path_mock.mock_calls

    for key in config_keys:
        assert mocker.call(key) in get_mock_calls and path_mock_calls


def test_set_config_str_key(mocker):
    """Test the set_config method when the input is a string."""

    cm_set_mock = mocker.patch("covalent._shared_files.config.ConfigManager.set")
    cm_write_config = mocker.patch("covalent._shared_files.config.ConfigManager.write_config")

    set_config("mock_section.mock_variable", "mock_value")

    cm_set_mock.assert_called_once_with("mock_section.mock_variable", "mock_value")
    cm_write_config.call_count == 2


def test_set_config_dict_key(mocker):
    """Test the set_config method when the input is a dictionary."""

    cm_set_mock = mocker.patch("covalent._shared_files.config.ConfigManager.set")
    cm_write_config = mocker.patch("covalent._shared_files.config.ConfigManager.write_config")

    set_config({"mock_section.mock_variable": "mock_value"})

    cm_set_mock.assert_called_once_with("mock_section.mock_variable", "mock_value")
    cm_write_config.call_count == 2


def test_generate_default_config(mocker):
    """Tests that the default configuration was loaded."""

    cm = ConfigManager()
    cm_deepcopy_mock = mocker.patch("covalent._shared_files.config.copy.deepcopy", return_value={})

    cm.generate_default_config()
    cm_deepcopy_mock.assert_called_once_with(DEFAULT_CONFIG)
    assert cm.config_data == DEFAULT_CONFIG


def test_read_config(mocker):
    """Test the read_config method for the config manager."""

    cm = ConfigManager()
    test_data = {"test": "test"}
    toml_load_mock = mocker.patch(
        "covalent._shared_files.config.toml.load", return_value=test_data
    )
    cm.read_config()
    toml_load_mock.assert_called_with(cm.config_file)
    assert cm.config_data == test_data


def test_get():
    """Test the get method for the config manager."""

    cm = ConfigManager()

    assert cm.get("dispatcher.port") == cm.config_data["dispatcher"]["port"]


def test_generate_default_config():
    """Test that the default configuration was loaded."""

    cm = ConfigManager()
    cm.generate_default_config()
    assert cm.config_data == DEFAULT_CONFIG
    assert cm.config_data is not DEFAULT_CONFIG


def test_reload_config(mocker):
    """Test the reload_config method."""

    cm_read_config = mocker.patch("covalent._shared_files.config.ConfigManager.read_config")
    reload_config()
    cm_read_config.assert_called_once_with()


def test_purge_config(mocker):
    """Test the purge_config method for config manager."""

    cm = ConfigManager()
    os_dir_mock = mocker.patch(
        "covalent._shared_files.config.os.path.dirname", return_value="mock_dir"
    )
    rmtree_mock = mocker.patch("covalent._shared_files.config.shutil.rmtree")
    cm.purge_config()
    os_dir_mock.assert_called_once_with(cm.config_file)
    rmtree_mock.assert_called_once_with("mock_dir", ignore_errors=True)


def test_get_config():
    """Test config retrieval function."""

    from covalent._shared_files.config import ConfigManager

    cm = ConfigManager()

    # Case 1 - Empty list
    assert get_config(entries=[]) == cm.config_data

    # Case 2 - List with one item
    assert get_config(entries=["dispatcher.port"]) == cm.config_data["dispatcher"]["port"]

    # Case 3 - String
    assert get_config(entries="dispatcher.port") == cm.config_data["dispatcher"]["port"]

    # Case 4 - List with > 1 items

    test_list = ["dispatcher.address", "dispatcher.port"]

    assert get_config(entries=test_list) == {
        "dispatcher.address": cm.config_data["dispatcher"]["address"],
        "dispatcher.port": cm.config_data["dispatcher"]["port"],
    }


def test_write_config(mocker):
    """Test the write_config method for config manager."""

    cm = ConfigManager()
    toml_dump_mock = mocker.patch("covalent._shared_files.config.toml.dump")
    open_mock = mocker.patch("covalent._shared_files.config.open")
    lock_mock = mocker.patch("fcntl.lockf")
    mock_file = open_mock.return_value.__enter__.return_value
    cm.write_config()
    toml_dump_mock.assert_called_once_with(cm.config_data, mock_file)
    open_mock.assert_called_once_with(cm.config_file, "w")
    lock_mock.assert_called_once()


def test_config_manager_set(mocker):
    """Test the set method in config manager."""

    cm = ConfigManager()
    cm.config_data = {"mock_section": {"mock_dir": "initial_value"}}
    cm.set("mock_section.mock_dir", "final_value")
    assert cm.config_data == {"mock_section": {"mock_dir": "final_value"}}

    cm.set("mock_section.new_mock_dir", "mock_value")
    assert cm.config_data == {
        "mock_section": {"mock_dir": "final_value", "new_mock_dir": "mock_value"}
    }

    cm.set("new_mock_section.new_mock_dir", "mock_value")
    assert cm.config_data == {
        "mock_section": {"mock_dir": "final_value", "new_mock_dir": "mock_value"},
        "new_mock_section": {"new_mock_dir": {"new_mock_dir": "mock_value"}},
    }
