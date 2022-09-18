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

from covalent._shared_files.config import (
    ClientConfigManager,
    ServerConfigManager,
    get_config,
    reload_config,
    set_config,
)
from covalent._shared_files.defaults import CMType, DefaultClientConfig, DefaultServerConfig

DEFAULT_CONFIG = {}
DEFAULT_CLIENT_CONFIG = asdict(DefaultClientConfig())
DEFAULT_SERVER_CONFIG = asdict(DefaultServerConfig())


@pytest.mark.parametrize(
    "dir_env, conf_dir",
    [
        ("COVALENT_CONFIG_DIR", "covalent/covalent.conf"),
        ("XDG_CONFIG_DIR", "covalent/covalent.conf"),
        ("HOME", ".config/covalent/covalent.conf"),
    ],
)
def test_client_config_manager_init_directory_setting(monkeypatch, dir_env, conf_dir):
    """Test the init method for the config manager."""

    with tempfile.TemporaryDirectory() as tmp_dir:
        monkeypatch.setenv(dir_env, tmp_dir)
        cm = ClientConfigManager()
        assert cm.config_file == f"{tmp_dir}/{conf_dir}"


@pytest.mark.parametrize(
    "dir_env, conf_dir",
    [
        ("COVALENT_CONFIG_DIR", "covalent/covalentd.conf"),
        ("XDG_CONFIG_DIR", "covalent/covalentd.conf"),
        ("HOME", ".config/covalent/covalentd.conf"),
    ],
)
def test_server_config_manager_init_directory_setting(monkeypatch, dir_env, conf_dir):
    """Test the init method for the config manager."""

    with tempfile.TemporaryDirectory() as tmp_dir:
        monkeypatch.setenv(dir_env, tmp_dir)
        cm = ServerConfigManager()
        assert cm.config_file == f"{tmp_dir}/{conf_dir}"


@pytest.mark.parametrize(
    "path_exists, write_config_called, update_config_called",
    [(False, True, False), (True, False, True)],
)
def test_client_config_manager_init_write_update_config(
    mocker, monkeypatch, path_exists, write_config_called, update_config_called
):
    """Test the init method for the client config manager."""

    config_keys = ["sdk.log_dir", "sdk.executor_dir"]

    with tempfile.TemporaryDirectory() as tmp_dir:
        monkeypatch.setenv("COVALENT_CONFIG_DIR", tmp_dir)
        update_config_mock = mocker.patch(
            "covalent._shared_files.config.ClientConfigManager.update_config"
        )
        write_config_mock = mocker.patch(
            "covalent._shared_files.config.ClientConfigManager.write_config"
        )
        get_mock = mocker.patch(
            "covalent._shared_files.config.ClientConfigManager.get", side_effect=config_keys
        )
        path_mock = mocker.patch("covalent._shared_files.config.Path.__init__", return_value=None)
        mocker.patch("os.path.exists", return_value=path_exists)

        cm = ClientConfigManager()
        assert hasattr(cm, "config_data")
        assert write_config_mock.called is write_config_called
        assert update_config_mock.called is update_config_called

    get_mock_calls = get_mock.mock_calls
    path_mock_calls = path_mock.mock_calls

    for key in config_keys:
        assert mocker.call(key) in get_mock_calls and path_mock_calls


@pytest.mark.parametrize(
    "path_exists, write_config_called, update_config_called",
    [(False, True, False), (True, False, True)],
)
def test_server_config_manager_init_write_update_config(
    mocker, monkeypatch, path_exists, write_config_called, update_config_called
):
    """Test the init method for the server config manager."""

    config_keys = [
        "service.cache_dir",
        "service.results_dir",
        "service.log_dir",
        "service.db_path",
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        monkeypatch.setenv("COVALENT_CONFIG_DIR", tmp_dir)
        update_config_mock = mocker.patch(
            "covalent._shared_files.config.ServerConfigManager.update_config"
        )
        write_config_mock = mocker.patch(
            "covalent._shared_files.config.ServerConfigManager.write_config"
        )
        get_mock = mocker.patch(
            "covalent._shared_files.config.ServerConfigManager.get", side_effect=config_keys
        )
        path_mock = mocker.patch("covalent._shared_files.config.Path.__init__", return_value=None)
        side_effect = None if path_exists else FileNotFoundError
        open_mock = mocker.patch("covalent._shared_files.config.open", side_effect=side_effect)

        cm = ServerConfigManager()
        assert hasattr(cm, "config_data")
        assert write_config_mock.called is write_config_called
        assert update_config_mock.called is update_config_called

    get_mock_calls = get_mock.mock_calls
    path_mock_calls = path_mock.mock_calls

    for key in config_keys:
        assert mocker.call(key) in get_mock_calls and path_mock_calls


def test_set_client_config_str_key(mocker):
    """Test the set_config method when the input is a string."""

    cm_set_mock = mocker.patch("covalent._shared_files.config.ClientConfigManager.set")
    cm_write_config = mocker.patch(
        "covalent._shared_files.config.ClientConfigManager.write_config"
    )

    set_config(CMType.CLIENT, "mock_section.mock_variable", "mock_value")

    cm_set_mock.assert_called_once_with("mock_section.mock_variable", "mock_value")
    cm_write_config.call_count == 2


def test_set_server_config_str_key(mocker):
    """Test the set_config method when the input is a string."""

    cm_set_mock = mocker.patch("covalent._shared_files.config.ServerConfigManager.set")
    cm_write_config = mocker.patch(
        "covalent._shared_files.config.ServerConfigManager.write_config"
    )

    set_config(CMType.SERVER, "mock_section.mock_variable", "mock_value")

    cm_set_mock.assert_called_once_with("mock_section.mock_variable", "mock_value")
    cm_write_config.call_count == 2


def test_set_client_config_dict_key(mocker):
    """Test the set_config method when the input is a dictionary."""

    cm_set_mock = mocker.patch("covalent._shared_files.config.ClientConfigManager.set")
    cm_write_config = mocker.patch(
        "covalent._shared_files.config.ClientConfigManager.write_config"
    )

    set_config(CMType.CLIENT, {"mock_section.mock_variable": "mock_value"})

    cm_set_mock.assert_called_once_with("mock_section.mock_variable", "mock_value")
    cm_write_config.call_count == 2


def test_set_server_config_dict_key(mocker):
    """Test the set_config method when the input is a dictionary."""

    cm_set_mock = mocker.patch("covalent._shared_files.config.ServerConfigManager.set")
    cm_write_config = mocker.patch(
        "covalent._shared_files.config.ServerConfigManager.write_config"
    )

    set_config(CMType.SERVER, {"mock_section.mock_variable": "mock_value"})

    cm_set_mock.assert_called_once_with("mock_section.mock_variable", "mock_value")
    cm_write_config.call_count == 2


def test_generate_default_client_config(mocker):
    """Tests that the default client configuration was loaded."""

    cm = ClientConfigManager()
    cm_deepcopy_mock = mocker.patch(
        "covalent._shared_files.config.copy.deepcopy", return_value=DEFAULT_CLIENT_CONFIG
    )

    cm.generate_default_config(DEFAULT_CLIENT_CONFIG)
    cm_deepcopy_mock.assert_called_once_with(DEFAULT_CLIENT_CONFIG)
    assert cm.config_data == DEFAULT_CLIENT_CONFIG


def test_generate_default_server_config(mocker):
    """Tests that the default server configuration was loaded."""

    cm = ServerConfigManager()
    cm_deepcopy_mock = mocker.patch(
        "covalent._shared_files.config.copy.deepcopy", return_value=DEFAULT_SERVER_CONFIG
    )

    cm.generate_default_config(DEFAULT_SERVER_CONFIG)
    cm_deepcopy_mock.assert_called_once_with(DEFAULT_SERVER_CONFIG)
    assert cm.config_data == DEFAULT_SERVER_CONFIG


def test_read_client_config(mocker):
    """Test the read_config method for the client config manager."""

    cm = ClientConfigManager()
    test_data = {"test": "test"}
    toml_load_mock = mocker.patch(
        "covalent._shared_files.config.toml.load", return_value=test_data
    )
    cm.read_config()
    toml_load_mock.assert_called_with(cm.config_file)
    assert cm.config_data == test_data


def test_read_server_config(mocker):
    """Test the read_config method for the server config manager."""

    cm = ServerConfigManager()
    test_data = {"test": "test"}
    toml_load_mock = mocker.patch(
        "covalent._shared_files.config.toml.load", return_value=test_data
    )
    cm.read_config()
    toml_load_mock.assert_called_with(cm.config_file)
    assert cm.config_data == test_data


def test_client_get():
    """Test the get method for the client config manager."""

    cm = ClientConfigManager()

    assert cm.get("server.port") == cm.config_data["server"]["port"]


def test_server_get():
    """Test the get method for the server config manager."""

    cm = ServerConfigManager()

    assert cm.get("service.port") == cm.config_data["service"]["port"]


def test_generate_default_client_config():
    """Test that the default client configuration was loaded."""

    cm = ClientConfigManager()
    cm.generate_default_config(DEFAULT_CLIENT_CONFIG)
    assert cm.config_data == DEFAULT_CLIENT_CONFIG
    assert cm.config_data is not DEFAULT_SERVER_CONFIG


def test_generate_default_server_config():
    """Test that the default server configuration was loaded."""

    cm = ServerConfigManager()
    cm.generate_default_config(DEFAULT_SERVER_CONFIG)
    assert cm.config_data == DEFAULT_SERVER_CONFIG
    assert cm.config_data is not DEFAULT_CLIENT_CONFIG


def test_reload_client_config(mocker):
    """Test the client reload_config method."""

    cm_read_config = mocker.patch("covalent._shared_files.config.ClientConfigManager.read_config")
    reload_config(CMType.CLIENT)
    cm_read_config.assert_called_once_with()


def test_reload_server_config(mocker):
    """Test the server reload_config method."""

    cm_read_config = mocker.patch("covalent._shared_files.config.ServerConfigManager.read_config")
    reload_config(CMType.SERVER)
    cm_read_config.assert_called_once_with()


def test_purge_client_config(mocker):
    """Test the purge_config method for client config manager."""

    cm = ClientConfigManager()
    os_dir_mock = mocker.patch(
        "covalent._shared_files.config.os.path.dirname", return_value="mock_dir"
    )
    rmtree_mock = mocker.patch("covalent._shared_files.config.shutil.rmtree")
    cm.purge_config()
    os_dir_mock.assert_called_once_with(cm.config_file)
    rmtree_mock.assert_called_once_with("mock_dir", ignore_errors=True)


def test_purge_server_config(mocker):
    """Test the purge_config method for server config manager."""

    cm = ServerConfigManager()
    os_dir_mock = mocker.patch(
        "covalent._shared_files.config.os.path.dirname", return_value="mock_dir"
    )
    rmtree_mock = mocker.patch("covalent._shared_files.config.shutil.rmtree")
    cm.purge_config()
    os_dir_mock.assert_called_once_with(cm.config_file)
    rmtree_mock.assert_called_once_with("mock_dir", ignore_errors=True)


def test_client_get_config():
    """Test client config retrieval function."""

    from covalent._shared_files.config import ClientConfigManager

    cm = ClientConfigManager()

    # Case 1 - Empty list
    assert get_config(CMType.CLIENT, entries=[]) == cm.config_data

    # Case 2 - List with one item
    assert get_config(CMType.CLIENT, entries=["server.port"]) == cm.config_data["server"]["port"]

    # Case 3 - String
    assert get_config(CMType.CLIENT, entries="server.port") == cm.config_data["server"]["port"]

    # Case 4 - List with > 1 items

    test_list = ["server.address", "server.port"]

    assert get_config(CMType.CLIENT, entries=test_list) == {
        "server.address": cm.config_data["server"]["address"],
        "server.port": cm.config_data["server"]["port"],
    }


def test_server_get_config():
    """Test client config retrieval function."""

    from covalent._shared_files.config import ServerConfigManager

    cm = ServerConfigManager()

    # Case 1 - Empty list
    assert get_config(CMType.SERVER, entries=[]) == cm.config_data

    # Case 2 - List with one item
    assert get_config(CMType.SERVER, entries=["service.port"]) == cm.config_data["service"]["port"]

    # Case 3 - String
    assert get_config(CMType.SERVER, entries="service.port") == cm.config_data["service"]["port"]

    # Case 4 - List with > 1 items

    test_list = ["service.address", "service.port"]

    assert get_config(CMType.SERVER, entries=test_list) == {
        "service.address": cm.config_data["service"]["address"],
        "service.port": cm.config_data["service"]["port"],
    }


def test_write_client_config(mocker):
    """Test the write_config method for client config manager."""

    cm = ClientConfigManager()
    toml_dump_mock = mocker.patch("covalent._shared_files.config.toml.dump")
    fnctl_lock_mock = mocker.patch("covalent._shared_files.config.fcntl.lockf")
    open_mock = mocker.patch("covalent._shared_files.config.open")
    mock_file = open_mock.return_value.__enter__.return_value
    cm.write_config()
    fnctl_lock_mock.assert_called_once()
    toml_dump_mock.assert_called_once_with(cm.config_data, mock_file)
    open_mock.assert_called_once_with(cm.config_file, "w")


def test_write_server_config(mocker):
    """Test the write_config method for server config manager."""

    cm = ServerConfigManager()
    toml_dump_mock = mocker.patch("covalent._shared_files.config.toml.dump")
    open_mock = mocker.patch("covalent._shared_files.config.open")
    lock_mock = mocker.patch("fcntl.lockf")
    mock_file = open_mock.return_value.__enter__.return_value
    cm.write_config()
    toml_dump_mock.assert_called_once_with(cm.config_data, mock_file)
    open_mock.assert_called_once_with(cm.config_file, "w")
    lock_mock.assert_called_once()


def test_client_config_manager_set(mocker):
    """Test the set method in client config manager."""

    cm = ClientConfigManager()
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


def test_server_config_manager_set(mocker):
    """Test the set method in server config manager."""

    cm = ServerConfigManager()
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
