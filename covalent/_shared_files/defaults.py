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
        "address": "0.0.0.0",
        "port": 48008,
        "cache_dir": (os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache"))
        + "/covalent",
        "results_dir": os.environ.get("COVALENT_RESULTS_DIR", "results"),
        "log_dir": (os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache"))
        + "/covalent",
    },
    "user_interface": {
        "address": "0.0.0.0",
        "port": 48008,
        "log_dir": (os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache"))
        + "/covalent",
        "dispatch_db": (os.environ.get("XDG_CACHE_HOME") or (os.environ["HOME"] + "/.cache"))
        + "/covalent/dispatch_db.sqlite",
    },
}

# Metadata which may influence execution behavior
_DEFAULT_CONSTRAINT_VALUES = {"executor": "local"}

# Going forward we may only want to return the executor field of DEFAULT_CONSTRAINT_VALUES
# The rest of those parameters will now be in this dictionary
_DEFAULT_CONSTRAINTS_DEPRECATED = {
    "schedule": False,
    "num_cpu": 1,
    "cpu_feature_set": [],
    "num_gpu": 0,
    "gpu_type": "",
    "gpu_compute_capability": [],
    "memory": "1G",
    "executor": "local",
    "time_limit": "00-00:00:00",
    "budget": 0,
    "conda_env": "",
}
