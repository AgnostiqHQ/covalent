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

import pkg_resources
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
    iter_entry_mock = mocker.patch(
        "pkg_resources.iter_entry_points",
        return_value=[pkg_resources.EntryPoint(name="test_name", module_name="test_module_name")],
    )
    load_mock = mocker.patch("pkg_resources.EntryPoint.load", return_value="test_module")

    nm = _NotificationManager()
    init_mock.assert_called_once_with()

    load_from_module_mock = mocker.patch(
        "covalent.notify._NotificationManager._load_plugin_from_module", return_value=None
    )

    nm._load_plugins()

    assert load_from_module_mock.call_count >= 1
    iter_entry_mock.assert_called_once_with("covalent.notify.notification_plugins")
    load_from_module_mock.assert_any_call("test_module")
    assert hasattr(nm, "notification_plugins_map")


@pytest.mark.parametrize(
    "well_defined,class_defined", [(True, True), (False, True), (True, False)]
)
def test_load_plugin(mocker, monkeypatch, well_defined, class_defined):
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
        if well_defined:
            plugin_name_str = 'notification_plugin_name = "TestNotifyPlugin"'
        else:
            plugin_name_str = ""

        if class_defined:
            class_def_str = "class TestNotifyPlugin(NotifyEndpoint):"
        else:
            class_def_str = "class SomethingElse():"

        plugin_file.write(
            """
from covalent.notify.notify import NotifyEndpoint

{plugin_name_str}

_NOTIFICATION_PLUGIN_DEFAULTS = {{
    "test_var": "test_value"
}}

{class_def_str}
    def notify(self, message):
        pass

    def dummy_func(self):
        pass

class DummyClass(NotifyEndpoint):
    def notify(self, message):
        pass
""".format(
                plugin_name_str=plugin_name_str, class_def_str=class_def_str
            )
        )

        plugin_file.flush()
        assert os.path.isfile(plugin_file.name)

        plugin_dir = Path(plugin_file.name).parent.resolve()
        module_name = Path(plugin_file.name).stem
        module_spec = importlib.util.spec_from_file_location(module_name, plugin_file.name)
        the_module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(the_module)

        nm._load_plugin_from_module(the_module)

        if well_defined and class_defined:
            write_mock.assert_called_once_with()
            assert module_name in nm.notification_plugins_map
            assert nm.notification_plugins_map[module_name].__name__ == "TestNotifyPlugin"
            assert "notify" in cm.config_data
            assert module_name in cm.config_data["notify"]
            assert "test_var" in cm.config_data["notify"][module_name]
            assert cm.config_data["notify"][module_name]["test_var"] == "test_value"
        else:
            write_mock.assert_not_called()
            assert not nm.notification_plugins_map
