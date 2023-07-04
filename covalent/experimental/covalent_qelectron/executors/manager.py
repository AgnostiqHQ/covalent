# Copyright 2023 Agnostiq Inc.
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

"""
Defines QExecutors and provides a "manager" to get all available QExecutors
"""

import importlib
import sys
from pathlib import Path
from typing import Any, Dict

from covalent._shared_files.config import update_config

from .clusters import QCluster
from .simulator import Simulator

_PLUGINS_PATH = Path(__file__).parent / "plugins"
_DEFAULTS_VARNAME = "_QEXECUTOR_PLUGIN_DEFAULTS"


class _QExecutorManager:
    """
    QExecutor manager to return a valid QExecutor which can be
    used as an argument to `qelectron` decorator.

    Initializing generates a list of available QExecutor plugins.
    """

    def __init__(self):
        # Dictionary mapping executor name to executor class
        self.executor_plugins_map: Dict[str, Any] = {
            "QCluster": QCluster,
            "Simulator": Simulator,
        }
        self.load_executors()

    def __new__(cls):
        # Singleton pattern for this class
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_executors(self) -> None:
        """
        Looks for `plugin.py` modules in the subdirectories of the given path and
        loads QExecutor classes from them.
        """

        # Iterate over all subdirectories of the plugins path except for those starting with "_" like "__pycache__"
        for plugin_dir in filter(lambda _p: _p.is_dir() and not _p.name.startswith("_"), _PLUGINS_PATH.iterdir()):

            # Get the Path of the plugin module
            plugin_module_path = list(plugin_dir.glob("*_plugin.py"))
            if not plugin_module_path:
                continue
            plugin_module_path = plugin_module_path[0]

            if plugin_module_path.exists():

                plugin_module_spec = importlib.util.spec_from_file_location(
                    plugin_module_path.stem,
                    plugin_module_path
                )
                plugin_module = importlib.util.module_from_spec(plugin_module_spec)

                sys.modules[plugin_module_path.stem] = plugin_module

                plugin_module_spec.loader.exec_module(plugin_module)

                self.populate_executors_map(plugin_module)

    def populate_executors_map(self, module_obj) -> None:
        """
        Validates modules containing potential QExecutor classes.
        Populates the `executor_plugins_map` dictionary and updates the config.
        """

        self.validate_module(module_obj)

        for qexecutor_cls_name in getattr(module_obj, "__all__"):
            self.executor_plugins_map[qexecutor_cls_name] = getattr(module_obj, qexecutor_cls_name)

        for qexecutor_cls_name, defaults_dict in getattr(module_obj, _DEFAULTS_VARNAME).items():
            update_config(
                {"qelectron": {qexecutor_cls_name: defaults_dict}},
                override_existing=False
            )

    def validate_module(self, module_obj) -> None:
        """
        Checks all of the following:
            - module exports plugin classes using `__all__`
            - module defines `_DEFAULTS_VARNAME`
            - exported plugin classes match the default parameters

        """
        if not hasattr(module_obj, "__all__"):
            return
        if not hasattr(module_obj, _DEFAULTS_VARNAME):
            return

        plugin_defaults = getattr(module_obj, _DEFAULTS_VARNAME)

        if set(module_obj.__all__).difference(set(plugin_defaults)):
            raise RuntimeError(
                f"Module missing default parameters in {module_obj.__file__}"
            )
        if set(plugin_defaults).difference(set(module_obj.__all__)):
            raise RuntimeError(
                f"Non-exported QExecutor class in default parameters in {module_obj.__file__}"
            )


qexecutor_manager = _QExecutorManager()
