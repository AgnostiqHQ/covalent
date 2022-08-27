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

"""Create custom sentinels and defaults for Covalent"""

import os
from configparser import ConfigParser

import dask.system

prefix_separator = ":"

parameter_prefix = f"{prefix_separator}parameter{prefix_separator}"
electron_list_prefix = f"{prefix_separator}electron_list{prefix_separator}"
electron_dict_prefix = f"{prefix_separator}electron_dict{prefix_separator}"
subscript_prefix = f"{prefix_separator}subscripted{prefix_separator}"
generator_prefix = f"{prefix_separator}generated{prefix_separator}"
sublattice_prefix = f"{prefix_separator}sublattice{prefix_separator}"
attr_prefix = f"{prefix_separator}attribute{prefix_separator}"
arg_prefix = f"{prefix_separator}arg{prefix_separator}"

# Default configuration settings
_DEFAULT_CONFIG = {
    "sdk": {
        "config_file": (
            os.environ.get("COVALENT_CONFIG_DIR")
            or os.environ.get("XDG_CONFIG_DIR")
            or os.environ["HOME"] + "/.config"
        )
        + "/covalent/covalent.conf",
        "log_dir": (
            os.environ.get("COVALENT_LOGDIR")
            or (os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache"))
        )
        + "/covalent",
        "log_level": os.environ.get("LOGLEVEL", "WARNING").lower(),
        "enable_logging": os.environ.get("COVALENT_LOG_TO_FILE", "false").lower(),
        "executor_dir": os.environ.get("COVALENT_EXECUTOR_DIR")
        or (os.environ.get("XDG_CONFIG_DIR") or (os.environ["HOME"] + "/.config"))
        + "/covalent/executor_plugins",
    },
    "dispatcher": {
        "address": "localhost",
        "port": 48008,
        "cache_dir": (os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache"))
        + "/covalent",
        "results_dir": os.environ.get("COVALENT_RESULTS_DIR", "results"),
        "log_dir": (os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache"))
        + "/covalent",
        "db_path": (os.environ.get("XDG_DATA_HOME"))
        or (os.environ["HOME"] + "/.local/share") + "/covalent/dispatcher_db.sqlite",
    },
    "dask": {
        "cache_dir": (os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache"))
        + "/covalent",
        "log_dir": (os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache"))
        + "/covalent",
        "mem_per_worker": "auto",
        "threads_per_worker": 1,
        "num_workers": dask.system.CPU_COUNT,
    },
    "workflow_data": {
        "storage_type": "local",
        "base_dir": (os.environ.get("XDG_DATA_HOME"))
        or (os.environ["HOME"] + "/.local/share") + "/covalent/workflow_data",
    },
    "user_interface": {
        "address": "localhost",
        "port": 48008,
        "dev_port": 49009,
        "log_dir": (os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache"))
        + "/covalent",
    },
}


def get_executor() -> dict:
    """
    Gets the executor based on whether Dask service is running.

    Returns:
        "dask" as the executor if Dask is running and "local" if Dask is not running.
    """
    config_parser = ConfigParser()
    config_file = _DEFAULT_CONFIG["sdk"]["config_file"]
    config_parser.read(config_file)
    return {"executor": "local"} if config_parser["sdk"]["no_cluster"] else {"executor": "dask"}


# Going forward we may only want to return the executor field of DEFAULT_CONSTRAINT_VALUES
# The rest of those parameters will now be in this dictionary
_DEFAULT_CONSTRAINT_VALUES = {
    "executor": get_executor(),
    "deps": {},
    "call_before": [],
    "call_after": [],
    "workflow_executor": get_executor(),
}

WAIT_EDGE_NAME = "!waiting_edge"
