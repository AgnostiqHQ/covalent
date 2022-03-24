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

"""Notification endpoint manager used to gather plugins."""

import importlib
import inspect
from pathlib import Path

import pkg_resources

from .._shared_files.config import update_config
from .._shared_files.logger import app_log


class _NotificationManager:
    """
    Notification endpoint manager.
    """

    def __init__(self) -> None:
        self._load_plugins()

    def _load_plugins(self) -> None:
        self.notification_plugins_map = {}

        # Load the webhook plugin
        plugin_dir = Path(__file__).parent.resolve()
        module_spec = importlib.util.spec_from_file_location(
            "webhook", f"{plugin_dir}/notification_plugins/webhook.py"
        )
        the_module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(the_module)
        self._load_plugin_from_module(the_module)

        # Load pip-installed plugins
        entry_points = pkg_resources.iter_entry_points("covalent.notify.notification_plugins")
        for entry in entry_points:
            the_module = entry.load()
            self._load_plugin_from_module(the_module)

    def _load_plugin_from_module(self, the_module) -> None:
        if not hasattr(the_module, "notification_plugin_name"):
            message = f"{the_module.__name__} does not seem to have a well-defined plugin class.\n"
            message += f"Specify the plugin class with 'notification_plugin_name = <plugin class name> in the {the_module.__name__} module."
            app_log.warning(message)
            return

        all_classes = inspect.getmembers(the_module, inspect.isclass)
        module_classes = [c[1] for c in all_classes if c[1].__module__ == the_module.__name__]
        plugin_class = [
            c for c in module_classes if c.__name__ == the_module.notification_plugin_name
        ]

        if len(plugin_class):
            plugin_class = plugin_class[0]
            short_name = the_module.__name__.split("/")[-1].split(".")[-1]
            self.notification_plugins_map[short_name] = plugin_class

            if hasattr(the_module, "_NOTIFICATION_PLUGIN_DEFAULTS"):
                default_params = {
                    "notify": {short_name: getattr(the_module, "_NOTIFICATION_PLUGIN_DEFAULTS")},
                }
                update_config(default_params, override_existing=False)
        else:
            message = f"Requested notification plugin {the_module.notification_plugin_name} was not found in {the_module.__name__}"
            app_log.warning(message)


_notification_manager = _NotificationManager()

for name in _notification_manager.notification_plugins_map:
    plugin_class = _notification_manager.notification_plugins_map[name]
    globals()[plugin_class.__name__] = plugin_class
