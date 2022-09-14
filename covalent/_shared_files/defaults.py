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
from builtins import list
from dataclasses import dataclass, field
from typing import Dict, List

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

WAIT_EDGE_NAME = "!waiting_edge"


def get_default_sdk_config():
    return {
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
        or (
            (os.environ.get("XDG_CONFIG_DIR") or (os.environ["HOME"] + "/.config"))
            + "/covalent/executor_plugins"
        ),
        "no_cluster": "false",
    }


def get_default_dispatcher_config():
    return {
        "address": "localhost",
        "port": int(os.environ.get("COVALENT_SVC_PORT"))
        if os.environ.get("COVALENT_SVC_PORT")
        else 48008,
        "cache_dir": os.environ.get("COVALENT_CACHE_DIR")
        or ((os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache")) + "/covalent"),
        "results_dir": os.environ.get("COVALENT_RESULTS_DIR", "results"),
        "log_dir": os.environ.get("COVALENT_LOGDIR")
        or ((os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache")) + "/covalent"),
        "db_path": os.environ.get("COVALENT_DATABASE")
        or (
            (os.environ.get("XDG_DATA_HOME") or (os.environ["HOME"] + "/.local/share"))
            + "/covalent/dispatcher_db.sqlite"
        ),
    }


def get_default_dask_config():
    return {
        "cache_dir": os.environ.get("COVALENT_CACHE_DIR")
        or ((os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache")) + "/covalent"),
        "log_dir": os.environ.get("COVALENT_LOGDIR")
        or ((os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache")) + "/covalent"),
        "mem_per_worker": "auto",
        "threads_per_worker": 1,
        "num_workers": dask.system.CPU_COUNT,
    }


def get_default_workflow_data_config():
    return {
        "storage_type": "local",
        "base_dir": os.environ.get("COVALENT_DATA_DIR")
        or (
            (os.environ.get("XDG_DATA_HOME") or (os.environ["HOME"] + "/.local/share"))
            + "/covalent/workflow_data"
        ),
    }


def get_default_ui_config():
    return {
        "address": "localhost",
        "port": int(os.environ.get("COVALENT_SVC_PORT"))
        if os.environ.get("COVALENT_SVC_PORT")
        else 48008,
        "dev_port": 49009,
        "log_dir": os.environ.get("COVALENT_LOGDIR")
        or ((os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache")) + "/covalent"),
    }


def get_default_executor() -> dict:
    """
    Gets the executor based on whether Dask service is running.

    Returns:
        "dask" as the executor if Dask is running and "local" if Dask is not running.
    """
    from .config import get_config

    return "local" if get_config("sdk.no_cluster") else "dask"


# Default configuration settings
@dataclass
class DefaultConfig:
    sdk: Dict = field(default_factory=get_default_sdk_config)
    dispatcher: Dict = field(default_factory=get_default_dispatcher_config)
    dask: Dict = field(default_factory=get_default_dask_config)
    workflow_data: Dict = field(default_factory=get_default_workflow_data_config)
    user_interface: Dict = field(default_factory=get_default_ui_config)


@dataclass
class DefaultMetadataValues:
    executor: str = field(default_factory=get_default_executor)
    deps: Dict = field(default_factory=dict)
    call_before: List = field(default_factory=list)
    call_after: List = field(default_factory=list)
    workflow_executor: str = field(default_factory=get_default_executor)
