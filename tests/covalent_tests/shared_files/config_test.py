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

import tempfile
from dataclasses import asdict

import pytest

from covalent._shared_files.config import ConfigManager, get_config, reload_config, set_config
from covalent._shared_files.defaults import DefaultConfig

DEFAULT_CONFIG = asdict(DefaultConfig())


@pytest.fixture
def config_manager():
    return ConfigManager()


@pytest.mark.parametrize(
    "dir_env, conf_dir",
    [
        ("COVALENT_CONFIG_DIR", "covalent.conf"),
        ("XDG_CONFIG_DIR", "covalent.conf"),
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
        "dispatcher.db_path",
    ]

    server_specific_config_keys = [
        "dispatcher.cache_dir",
        "dispatcher.results_dir",
        "dispatcher.log_dir",
        "user_interface.log_dir",
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
        assert (mocker.call(key) in get_mock_calls) and (mocker.call(key) in path_mock_calls)

    # check if creation doesn't happen during config manager init
    for key in server_specific_config_keys:
        assert (mocker.call(key) not in get_mock_calls) and (
            mocker.call(key) not in path_mock_calls
        )


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


def test_generate_default_config(mocker, config_manager):
    """Tests that the default configuration was loaded."""

    cm = config_manager
    cm_deepcopy_mock = mocker.patch("covalent._shared_files.config.copy.deepcopy", return_value={})

    cm.generate_default_config()
    cm_deepcopy_mock.assert_called_once_with(DEFAULT_CONFIG)
    assert cm.config_data == DEFAULT_CONFIG


def test_read_config(mocker, config_manager):
    """Test the read_config method for the config manager."""

    cm = config_manager
    test_data = {"test": "test"}
    toml_load_mock = mocker.patch(
        "covalent._shared_files.config.toml.load", return_value=test_data
    )
    cm.read_config()
    toml_load_mock.assert_called_with(cm.config_file)
    assert cm.config_data == test_data


def test_get(config_manager):
    """Test the get method for the config manager."""

    cm = config_manager

    assert cm.get("dispatcher.port") == cm.config_data["dispatcher"]["port"]


def test_generate_default_config(config_manager):
    """Test that the default configuration was loaded."""

    cm = config_manager
    cm.generate_default_config()
    assert cm.config_data == DEFAULT_CONFIG
    assert cm.config_data is not DEFAULT_CONFIG


def test_reload_config(mocker):
    """Test the reload_config method."""

    cm_read_config = mocker.patch("covalent._shared_files.config.ConfigManager.read_config")
    reload_config()
    cm_read_config.assert_called_once_with()


def test_purge_config(mocker, config_manager):
    """Test the purge_config method for config manager."""

    cm = config_manager
    os_dir_mock = mocker.patch(
        "covalent._shared_files.config.os.path.dirname", return_value="mock_dir"
    )
    rmtree_mock = mocker.patch("covalent._shared_files.config.shutil.rmtree")
    cm.purge_config()
    os_dir_mock.assert_called_once_with(cm.config_file)
    rmtree_mock.assert_called_once_with("mock_dir", ignore_errors=True)


def test_get_config(config_manager):
    """Test config retrieval function."""

    cm = config_manager

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


def test_write_config(mocker, config_manager):
    """Test the write_config method for config manager."""

    cm = config_manager
    toml_dump_mock = mocker.patch("covalent._shared_files.config.toml.dump")
    open_mock = mocker.patch("covalent._shared_files.config.open")
    mock_file = open_mock.return_value.__enter__.return_value
    cm.write_config()
    toml_dump_mock.assert_called_once_with(cm.config_data, mock_file)
    open_mock.assert_called_once_with(cm.config_file, "w")


def test_update_config(mocker):
    """Test the update_config method for config manager."""

    cm = ConfigManager()

    cm.config_file = "mock_config_file"
    cm.config_data = {"mock_section": {"mock_dir": "initial_value"}}
    # Cannot mock `update_nested_dict`` since it's defined within the function

    mock_filelock = mocker.patch("covalent._shared_files.config.filelock.FileLock")
    mock_open = mocker.patch("covalent._shared_files.config.open")
    mock_toml_load = mocker.patch("covalent._shared_files.config.toml.load")

    cm.write_config = mocker.Mock()

    cm.update_config()

    mock_filelock.assert_called_once_with("mock_config_file.lock", timeout=1)
    mock_open.assert_called_once_with("mock_config_file", "r+")
    mock_toml_load.assert_called_once_with(mock_open.return_value.__enter__.return_value)

    cm.write_config.assert_called_once()


def test_config_manager_set(mocker, config_manager):
    """Test the set method in config manager."""

    cm = config_manager
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
