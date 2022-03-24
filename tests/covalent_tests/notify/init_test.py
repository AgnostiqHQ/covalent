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

"""Tests for notification init file."""

import importlib
import os
import tempfile
from pathlib import Path

import pytest

from covalent._shared_files.config import _config_manager, _ConfigManager
from covalent.notify import _NotificationManager


def test_notify_manager_init(mocker):
    """Test the init method of the notification manager class object."""

    load_plugins_mock = mocker.patch(
        "covalent.notify._NotificationManager._load_plugins", return_value=None
    )

    _NotificationManager()

    load_plugins_mock.assert_called_once_with()


def test_load_plugins(mocker):
    """Test the load_plugins method of the notification manager object."""

    init_mock = mocker.patch("covalent.notify._NotificationManager.__init__", return_value=None)

    nm = _NotificationManager()
    init_mock.assert_called_once_with()

    load_from_module_mock = mocker.patch(
        "covalent.notify._NotificationManager._load_plugin_from_module", return_value=None
    )

    nm._load_plugins()

    load_from_module_mock.assert_called()

    assert load_from_module_mock.call_count >= 1
    assert hasattr(nm, "notification_plugins_map")


def test_load_plugin(mocker, monkeypatch):
    """Test the load_plugin_from_module method of the notification manager object."""

    init_mock = mocker.patch("covalent.notify._NotificationManager.__init__", return_value=None)
    nm = _NotificationManager()
    init_mock.assert_called_once_with()
    nm.notification_plugins_map = {}

    init_config_mock = mocker.patch(
        "covalent._shared_files.config._ConfigManager.__init__", return_value=None
    )
    cm = _ConfigManager()
    init_config_mock.assert_called_once_with()
    cm.config_file = _config_manager.config_file
    cm.config_data = {}
    # Work with an empty config dict
    monkeypatch.setattr("covalent._shared_files.config._config_manager", cm)
    # Ensure this dict doesn't overwrite the user config
    write_mock = mocker.patch(
        "covalent._shared_files.config._ConfigManager.write_config", return_value=None
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py") as plugin_file:
        plugin_file.write(
            """
from covalent.notify.notify import NotifyEndpoint

notification_plugin_name = "TestNotifyPlugin"

_NOTIFICATION_PLUGIN_DEFAULTS = {
    "test_var": "test_value"
}

class TestNotifyPlugin(NotifyEndpoint):
    def notify(self, message):
        pass

    def dummy_func(self):
        pass

class DummyClass(NotifyEndpoint):
    def notify(self, message):
        pass
"""
        )

        plugin_file.flush()
        assert os.path.isfile(plugin_file.name)

        plugin_dir = Path(plugin_file.name).parent.resolve()
        module_name = Path(plugin_file.name).stem
        module_spec = importlib.util.spec_from_file_location(module_name, plugin_file.name)
        the_module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(the_module)

        nm._load_plugin_from_module(the_module)

        write_mock.assert_called_once_with()
        assert module_name in nm.notification_plugins_map
        assert nm.notification_plugins_map[module_name].__name__ == "TestNotifyPlugin"
        assert "notify" in cm.config_data
        assert module_name in cm.config_data["notify"]
        assert "test_var" in cm.config_data["notify"][module_name]
        assert cm.config_data["notify"][module_name]["test_var"] == "test_value"
