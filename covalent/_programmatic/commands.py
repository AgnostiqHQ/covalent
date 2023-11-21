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
import time
from typing import Any, Dict, Optional

import click
import psutil

from covalent_dispatcher._cli.service import _read_pid, start, stop

from .._shared_files import logger
from .._shared_files.config import get_config

app_log = logger.app_log


def _call_cli_command(func: click.Command, **kwargs: Dict[str, Any]) -> Any:
    """Call the CLI command ``func`` with the specified kwargs."""
    ctx = click.Context(func)
    ctx.invoke(func, **kwargs)


def covalent_is_running() -> bool:
    """Return True if the Covalent server is in a ready state."""
    pid = _read_pid(get_config("dispatcher.cache_dir") + "/ui.pid")
    return (
        pid != -1
        and psutil.pid_exists(pid)
        and get_config("dispatcher.address") != ''
        and get_config("dispatcher.port") != ''
    )


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
) -> None:
    """Start the Covalent server. Wrapper for the `covalent start` CLI command.

    Args:
        develop: Start local server in develop mode. Defaults to False.
        port: Local server port number. Defaults to 48008.
        mem_per_worker: Memory limit per worker in GB. Defaults to auto.
        workers: Number of Dask workers. Defaults to 8.
        threads_per_worker: Number of threads per Dask worker. Defaults to 1.
        ignore_migrations: Start server without database migrations. Defaults to False.
        no_cluster: Start server without Dask cluster. Defaults to False.
        no_triggers: Start server without a triggers server. Defaults to False.
        triggers_only: Start only the triggers server. Defaults to False.
    """
    if covalent_is_running():
        return

    kwargs = {
        "develop": develop,
        "port": port or get_config("dispatcher.port"),
        "mem_per_worker": mem_per_worker or get_config("dask.mem_per_worker"),
        "workers": workers or get_config("dask.num_workers"),
        "threads_per_worker": threads_per_worker or get_config("dask.threads_per_worker"),
        "ignore_migrations": ignore_migrations,
        "no_cluster": no_cluster,
        "no_triggers": no_triggers,
        "triggers_only": triggers_only,
    }

    _call_cli_command(start, **kwargs)

    while not covalent_is_running():
        app_log.debug("Waiting for Covalent Server to be to dispatch-ready...")
        time.sleep(1)


def covalent_stop() -> None:
    """Stop the Covalent server. Wrapper for the `covalent stop` CLI command."""
    if not covalent_is_running():
        return

    _call_cli_command(stop)

    while covalent_is_running():
        app_log.debug("Waiting for Covalent Server to stop...")
        time.sleep(1)
