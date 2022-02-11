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

from covalent.executor import _executor_manager, _ExecutorManager


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


# def test_executor_manager_generate_plugins_list(mocker):
#     """Test the generate plugins list method of the executor manager object."""

#     init_mock = mocker.patch("covalent.executor._ExecutorManager.__init__", return_value=None)

#     em = _ExecutorManager()
#     init_mock.called_once_with()

#     load_executors_mock = mocker.patch("covalent.executor._ExecutorManager._load_executors")
#     os_path_join = mocker.patch("os.path.join", side_effect=["plugin_path", "default_plugin_path", "user_plugin_path"])
#     em.generate_plugins_list()

#     assert load_executors_mock.mock_calls == [mocker.call("plugin_path"), mocker.call("default_plugin_path")]
