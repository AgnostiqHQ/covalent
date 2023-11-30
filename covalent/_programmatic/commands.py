# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Functions providing programmatic access to Covalent CLI commands."""
import subprocess
from typing import List, Optional

import psutil

from .._shared_files import logger
from .._shared_files.config import get_config

__all__ = ["is_covalent_running", "covalent_start", "covalent_stop"]


app_log = logger.app_log

_MISSING_SERVER_WARNING = "Covalent has not been installed with the server component."


def _call_cli_command(cmd: List[str], *, quiet: bool = False) -> subprocess.CompletedProcess:
    """
    Call a CLI command with the specified kwargs.

    Args:
        func: The CLI command to call.
        quiet: Suppress stdout. Defaults to :code:`False`.
    """

    if quiet:
        return subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

    return subprocess.run(cmd, check=True)


def is_covalent_running() -> bool:
    """
    Check if the Covalent server is running.

    Returns:
        :code:`True` if the Covalent server is in a ready state, :code:`False` otherwise.
    """
    try:
        from covalent_dispatcher._cli.service import _read_pid

        pid = _read_pid(get_config("dispatcher.cache_dir") + "/ui.pid")
        return (
            pid != -1
            and psutil.pid_exists(pid)
            and get_config("dispatcher.address") != ""
            and get_config("dispatcher.port") != ""
        )

    except ModuleNotFoundError:
        # If the covalent_dispatcher is not installed, assume Covalent is not running.
        app_log.warning(_MISSING_SERVER_WARNING)
        return False


def covalent_start(
    develop: bool = False,
    port: Optional[str] = None,
    mem_per_worker: Optional[str] = None,
    workers: Optional[int] = None,
    threads_per_worker: Optional[int] = None,
    ignore_migrations: bool = False,
    no_cluster: bool = False,
    no_triggers: bool = False,
    triggers_only: bool = False,
    *,
    quiet: bool = False,
) -> None:
    """
    Start the Covalent server. Wrapper for the :code:`covalent start` CLI command.
    This function returns immediately if the local Covalent server is already running.

    Args:
        develop: Start local server in develop mode. Defaults to :code:`False`.
        port: Local server port number. Defaults to :code:`"48008"`.
        mem_per_worker: Memory limit per worker in GB. Defaults to auto.
        workers: Number of Dask workers. Defaults to 8.
        threads_per_worker: Number of threads per Dask worker. Defaults to 1.
        ignore_migrations: Start server without database migrations. Defaults to :code:`False`.
        no_cluster: Start server without Dask cluster. Defaults to :code:`False`.
        no_triggers: Start server without a triggers server. Defaults to :code:`False`.
        triggers_only: Start only the triggers server. Defaults to :code:`False`.
        quiet: Suppress stdout. Defaults to :code:`False`.
    """

    if is_covalent_running():
        msg = "Covalent server is already running."
        if not quiet:
            print(msg)

        app_log.debug(msg)
        return

    flags = {
        "--develop": develop,
        "--ignore-migrations": ignore_migrations,
        "--no-cluster": no_cluster,
        "--no-triggers": no_triggers,
        "--triggers-only": triggers_only,
    }

    args = {
        "--port": port or get_config("dispatcher.port"),
        "--mem-per-worker": mem_per_worker or get_config("dask.mem_per_worker"),
        "--workers": workers or get_config("dask.num_workers"),
        "--threads-per-worker": threads_per_worker or get_config("dask.threads_per_worker"),
    }

    cmd = ["covalent", "start"]
    cmd.extend(flag for flag, value in flags.items() if value)

    for arg, value in args.items():
        cmd.extend((arg, str(value)))

    # Run the `covalent start [OPTIONS]` command.
    app_log.debug("Starting Covalent server programmatically...")
    _call_cli_command(cmd, quiet=quiet)


def covalent_stop(*, quiet: bool = False) -> None:
    """
    Stop the Covalent server. Wrapper for the :code:`covalent stop` CLI command.
    This function returns immediately if the local Covalent server is not running.

    Args:
        quiet: Suppress stdout. Defaults to :code:`False`.
    """

    if not is_covalent_running():
        msg = "Covalent server is not running."
        if not quiet:
            print(msg)

        app_log.debug(msg)
        return

    # Run the `covalent stop` command.
    app_log.debug("Stopping Covalent server programmatically...")
    _call_cli_command(["covalent", "stop"], quiet=quiet)
