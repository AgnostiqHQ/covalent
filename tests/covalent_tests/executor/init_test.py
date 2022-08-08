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

"""Tests for Covalent executor init file."""

from unittest.mock import MagicMock

import pytest

from covalent.executor import BaseExecutor, _executor_manager, _ExecutorManager


def test_get_executor_local(mocker):
    """Test that config is reloaded when the get_executor method is called for the local executor."""

    update_config_mock = mocker.patch("covalent.executor.update_config")
    _executor_manager.get_executor(name="local")
    update_config_mock.assert_called_once_with()


def test_executor_manager_init(mocker):
    """Test the init method of the executor manager object."""

    generate_plugins_list_mock = mocker.patch(
        "covalent.executor._ExecutorManager.generate_plugins_list"
    )

    _ExecutorManager()
    generate_plugins_list_mock.assert_called_once_with()


def test_executor_manager_generate_plugins_list(mocker):
    """Test the generate plugins list method of the executor manager object."""

    init_mock = mocker.patch("covalent.executor._ExecutorManager.__init__", return_value=None)

    em = _ExecutorManager()
    init_mock.called_once_with()

    load_executors_mock = mocker.patch("covalent.executor._ExecutorManager._load_executors")

    os_path_dirname_mock = mocker.patch("os.path.dirname", return_value="covalent")
    os_path_join_mock = mocker.patch("os.path.join", return_value="pkg_plugins_path")
    get_config_mock = mocker.patch(
        "covalent.executor.get_config", return_value="user_plugins_path"
    )
    load_installed_plugins_mock = mocker.patch(
        "covalent.executor._ExecutorManager._load_installed_plugins"
    )

    em.generate_plugins_list()
    os_path_join_mock.assert_called_once_with("covalent", "executor_plugins")
    get_config_mock.assert_called_once_with("sdk.executor_dir")

    assert load_executors_mock.mock_calls == [
        mocker.call("pkg_plugins_path"),
        mocker.call("user_plugins_path"),
    ]
    load_installed_plugins_mock.called_once_with()


def test_get_executor(mocker):
    """Test get executor method in executor manager."""

    class MockExecutor(BaseExecutor):
        def run(self):
            pass

    def plugin_mock(**kwargs):
        return "plugin map func called"

    mocker.patch("covalent.executor._ExecutorManager.__init__", return_value=None)

    # Case 1 - name is BaseExecutor type
    em = _ExecutorManager()
    resp = em.get_executor(MockExecutor())
    assert isinstance(resp, MockExecutor)

    # Case 2 - name is str and in executor_plugin_map
    get_config_mock = mocker.patch("covalent.executor.get_config", return_value={"test_arg": 1})
    update_config_mock = mocker.patch("covalent.executor.update_config")

    em.executor_plugins_map = {"mock_name": plugin_mock}
    resp = em.get_executor(name="mock_name")
    update_config_mock.assert_called_once_with()
    get_config_mock.assert_called_once_with("executors.mock_name")
    assert resp == "plugin map func called"

    # Case 3 - name is str and not in executor_plugin_map
    with pytest.raises(ValueError):
        em.get_executor(name="non-existent")

    # Case4 - name is neither str or BaseExecutor type
    with pytest.raises(TypeError):
        em.get_executor(name=3)


def test_load_installed_plugins(mocker):
    """Test load installed plugins."""

    mocker.patch("covalent.executor._ExecutorManager.__init__", return_value=None)
    populate_executor_map_from_module_mock = mocker.patch(
        "covalent.executor._ExecutorManager._load_installed_plugins"
    )
    em = _ExecutorManager()
    em._load_installed_plugins()
    populate_executor_map_from_module_mock.assert_called()


def test_warning_when_plugin_name_is_invalid(mocker):
    """Test executor plugin name validator"""
    em = _ExecutorManager()
    the_module = MagicMock()
    the_module.__name__ = "test_module"
    em._is_plugin_name_valid = MagicMock(return_value=False)
    app_log_mock = mocker.patch("covalent.executor.app_log")

    em._populate_executor_map_from_module(the_module)

    app_log_mock.warning.assert_called_once()
