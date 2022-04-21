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

import copy
import os
import shutil
from functools import reduce
from operator import getitem
from pathlib import Path
from typing import Any, Dict, List, MutableMapping, Optional, Union

import toml
from dotenv import dotenv_values, find_dotenv, load_dotenv, set_key

"""Configuration manager."""

CONFIG_FILE_NAME = ".env"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) + "/../.."
HOME_PATH = os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache")
COVALENT_CACHE_DIR = os.path.join(HOME_PATH, "covalent")

# TODO: add tests for below functions


def dict_get(dictionary, key, default=None):
    value = dictionary
    try:
        for key in key.split("."):
            if isinstance(value, dict):
                value = value[key]
                continue
            else:
                return default
    except KeyError:
        return default
    else:
        return value


def dict_set(dictionary, key, value):
    keys = key.split(".")
    latest = keys.pop()
    for k in keys:
        dictionary = dictionary.setdefault(k, {})
    dictionary[latest] = value


def dict_flatten(d: MutableMapping, parent_key: str = "", sep: str = ".") -> MutableMapping:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(dict_flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class _ConfigManager:
    """Configuration manager class object.

    This class is used to manage an in-memory copy of a TOML configuration file.
    """

    def __init__(self) -> None:

        self.env_path = os.environ.get("ENV_DEST_DIR") or COVALENT_CACHE_DIR
        self.config_file = os.path.join(self.env_path, CONFIG_FILE_NAME)

        if not os.path.exists(self.env_path):
            Path(self.env_path).mkdir(parents=True, exist_ok=True)

        # ensure .env exists, if not copy from .env.example
        self.ensure_config_file_exists()

        # load .env values into os.environ or use explicitly set environment vars
        load_dotenv(self.config_file)

    @property
    def config_data(self):
        # should yield the same result as doing load_env()
        # environment vars take precedence, then config values
        config = {}
        config_file_values = dotenv_values(self.config_file)

        environment_vars = {**config_file_values, **os.environ}

        for key in config_file_values.keys():
            dict_set(config, key, environment_vars[key] or "")
        return config

    def ensure_config_file_exists(self):
        if not find_dotenv(self.config_file):
            shutil.copyfile(
                f"{PROJECT_ROOT}/covalent/.env.example",
                self.config_file,
            )

    def update_config(
        self, new_entries: Optional[Dict] = None, override_existing: bool = True
    ) -> None:
        """
        Update the exising configuration dictionary with the configuration stored in file.
            Optionally, update configuration data with an input dict.

        Args:
            new_entries: Dictionary of new entries added or updated in the config.
            override_existing: If True (default), config values from the config file
                or the input dictionary (new_entries) take precedence over any existing
                values in the config.

        Returns:
            None
        """

        if new_entries:
            flattened_config_dict = dict_flatten(new_entries)
            for key, value in flattened_config_dict.items():
                self.set(key, value)

    def purge_config(self) -> None:
        """
        Purge the configuration directory.

        Args:
            None

        Returns:
            None
        """

        # remove .env config file which may live in an arbitrary folder
        try:
            os.remove(self.config_file)
        except FileNotFoundError:
            pass

        # remove covalent cache directory with log files, and supervisord.conf
        shutil.rmtree(COVALENT_CACHE_DIR, ignore_errors=True)

        # attempt to remove legacy .env file
        try:
            os.remove(os.path.join(PROJECT_ROOT, CONFIG_FILE_NAME))
        except FileNotFoundError:
            pass

    def get(self, key: str) -> Any:
        """
        Return a value given a dictionary key.

        Args:
            key: Key value in period-delimited format, e.g., config[dispatcher][port]
                 is queried by passing "legacy_dispatcher.port" as the key.

        Returns:
            value: The corresponding configuration value, usually a string or int.
        """
        try:
            value = dict_get(self.config_data, key)
        except KeyError as e:
            value = None
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a key-value pair in the configuration dictionary.

        Args:
            key: Key value in period-delimited format.
            value: The corresponding configuration setting.

        Returns:
            None
        """
        set_key(self.config_file, key, str(value))


_config_manager = _ConfigManager()


def set_config(new_config: Union[Dict, str], new_value: Any = None) -> None:
    """
    Update the configuration.

    Users may pass a dictionary of new settings, or a string key with a value to set
    a single configuration setting.

    Args:
        new_config: The new configuration dictionary, or a string key name.
        new_value: A new configuration value, if the first argument is a string.

    Returns:
        None
    """

    if isinstance(new_config, str):
        _config_manager.set(new_config, new_value)
    else:
        for key, value in new_config.items():
            _config_manager.set(key, value)


def get_config(entries: Union[str, List] = []) -> Union[Dict, Union[str, int]]:
    """
    Return a configuration setting.

    Invocation with no arguments returns the full configuration description; with a
    list of arguments returns a dictionary of configuration settings; with a string
    key name returns the corresponding value for a single setting.

    Args:
        entries: A string or list of strings specifying key names.

    Returns:
        config: A dictionary or string describing the corresponding configuration
                settings.
    """

    if isinstance(entries, List) and len(entries) == 0:
        # If no arguments are passed, return the full configuration as a dict
        return _config_manager.config_data
    elif isinstance(entries, List) and len(entries) == 1:
        # If the argument is a single key in a List, return the corresponding value
        return _config_manager.get(entries[0])
    elif isinstance(entries, str):
        # If the argument is a string key, return the corresponding value
        return _config_manager.get(entries)
    else:
        # If a set of keys are passed, return a corresponding dict of key-value pairs
        values = [_config_manager.get(entry) for entry in entries]
        return dict(zip(entries, values))


def update_config(new_entries: Optional[Dict] = None, override_existing: bool = True) -> None:
    """
    Read the configuration from the TOML file and append to default
        (or existing) configuration. Optionally, update configuration
        data with an input dict.

    Args:
        new_entries: Dictionary of new entries added or updated in the config
        defaults: If False (which is the default), default values do not overwrite
            existing entries.

    Returns:
        None
    """

    _config_manager.update_config(new_entries, override_existing)
