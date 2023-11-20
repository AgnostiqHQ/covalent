"""Functions providing programmatic access to Covalent CLI commands."""
import time
from typing import Any, Dict, Optional

import click
import psutil

from covalent import get_config
from covalent._shared_files import logger

from ._cli.service import _read_pid, start, stop

app_log = logger.app_log


def _call_cli_command(func: click.Command, **kwargs: Dict[str, Any]) -> Any:
    """Call the CLI command ``func`` with the specified kwargs."""
    ctx = click.Context(func)
    ctx.invoke(func, **kwargs)


def covalent_is_running() -> bool:
    """Return True if the Covalent server is in a ready state."""
    pid = _read_pid(get_config("dispatcher.cache_dir") + "/ui.pid")
    return (
        psutil.pid_exists(pid)
        and pid != -1
        and get_config("dispatcher.address")
        and get_config("dispatcher.port")
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
):
    """
    Start the Covalent server. Wrapper for the `covalent start` CLI command.
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


def covalent_stop():
    """
    Stop the Covalent server. Wrapper for the `covalent stop` CLI command.
    """
    if not covalent_is_running():
        return

    _call_cli_command(stop)

    while covalent_is_running():
        app_log.debug("Waiting for Covalent Server to stop...")
        time.sleep(1)
