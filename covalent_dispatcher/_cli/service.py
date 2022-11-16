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

"""Covalent CLI Tool - Service Management."""


import asyncio
import contextlib
import json
import os
import shutil
import socket
import time
from subprocess import DEVNULL, Popen
from typing import Optional

import click
import dask.system
import psutil
import requests
from distributed.comm import unparse_address
from distributed.core import connect, rpc

from covalent._shared_files.config import ConfigManager, get_config, set_config

from .._db.datastore import DataStore
from .migrate import migrate_pickled_result_object

cm = ConfigManager()

UI_PIDFILE = get_config("dispatcher.cache_dir") + "/ui.pid"
UI_LOGFILE = get_config("user_interface.log_dir") + "/covalent_ui.log"
UI_SRVDIR = f"{os.path.dirname(os.path.abspath(__file__))}/../../covalent_ui"

MIGRATION_WARNING_MSG = "Covalent not started. The database needs to be upgraded."
MIGRATION_COMMAND_MSG = (
    '   (use "covalent db migrate" to run database migrations and then retry "covalent start")'
)


def _read_pid(filename: str) -> int:
    """
    Read the process ID from file.

    Args:
        filename: The path to the file to read the process ID from.

    Returns:
        The process ID.
    """

    try:
        pid = int(open(filename, "r").readline())
    except FileNotFoundError:
        pid = -1

    return pid


def _rm_pid_file(filename: str) -> None:
    """
    Remove a process ID file safely.

    Args:
        filename: The path to the file that will be removed.

    Returns:
        None
    """

    if os.path.isfile(filename):
        os.remove(filename)


def _port_from_pid(pid: int) -> Optional[int]:
    """
    Return the port in use by a process.

    Args:
        pid: Process ID.

    Returns:
        port: Port in use by the process.
    """

    if psutil.pid_exists(pid):
        return psutil.Process(pid).connections()[0].laddr.port
    return None


def _next_available_port(requested_port: int) -> int:
    """
    Return the next available port not in use.

    Args:
        requested_port: Port requested for a socket.

    Returns:
        assigned_port: Next available port greater than or equal to the requested port.
    """

    avail_port_found = False
    try_port = requested_port

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    while not avail_port_found:
        try:
            sock.bind(("localhost", try_port))
            avail_port_found = True
        except:
            try_port += 1

    sock.close()
    assigned_port = try_port

    if assigned_port != requested_port:
        click.echo(
            f"Port {requested_port} was already in use. Using port {assigned_port} instead."
        )

    return assigned_port


def _is_server_running() -> bool:
    """Check status of the Covalent server.

    Returns:
        status: Status of whether the server is running.
    """
    return _read_pid(UI_PIDFILE) != -1


def _graceful_start(
    server_root: str,
    pidfile: str,
    logfile: str,
    port: int,
    no_cluster: bool,
    develop: bool = False,
) -> int:
    """
    Gracefully start a Fast API app.

    Args:
        server_root: Directory where app.py is located.
        pidfile: Process ID file for the server.
        logfile: Log file for the server.
        port: Port requested to be used by the server.
        no_cluster: Dask cluster is not used.
        develop: Start the server in developer mode.

    Returns:
        port: Port assigned to the server.
    """
    pid = _read_pid(pidfile)
    if psutil.pid_exists(pid):
        port = get_config("user_interface.port")
        click.echo(f"Covalent server is already running at http://localhost:{port}.")
        return port

    _rm_pid_file(pidfile)

    pypath = f"PYTHONPATH={UI_SRVDIR}/../tests:$PYTHONPATH" if develop else ""
    dev_mode_flag = "--develop" if develop else ""
    no_cluster_flag = "--no-cluster" if no_cluster else ""
    port = _next_available_port(port)
    launch_str = (
        f"{pypath} python app.py {dev_mode_flag} --port {port} {no_cluster_flag} >> {logfile} 2>&1"
    )

    proc = Popen(launch_str, shell=True, stdout=DEVNULL, stderr=DEVNULL, cwd=server_root)
    pid = proc.pid

    with open(pidfile, "w") as PIDFILE:
        PIDFILE.write(str(pid))

    # Wait until the server actually starts listening on the port
    dispatcher_addr = f"http://localhost:{port}"
    up = False
    while not up:
        try:
            requests.get(dispatcher_addr, timeout=1)
            up = True
        except requests.exceptions.ConnectionError as err:
            time.sleep(1)

    click.echo(f"Covalent server has started at http://localhost:{port}")
    return port


def _terminate_child_processes(pid: int) -> None:
    """For a given process, find all the child processes and terminate them.

    Args:
        pid: Process ID file for the main server process.

    Returns:
        None
    """
    for child_proc in psutil.Process(pid).children(recursive=True):
        with contextlib.suppress(psutil.NoSuchProcess):
            child_proc.kill()
            child_proc.wait()


def _graceful_shutdown(pidfile: str) -> None:
    """
    Gracefully shut down a server given a process ID.

    Args:
        pidfile: Process ID file for the server.

    Returns:
        None
    """

    pid = _read_pid(pidfile)
    if psutil.pid_exists(pid):
        proc = psutil.Process(pid)
        _terminate_child_processes(pid)

        with contextlib.suppress(psutil.NoSuchProcess):
            proc.terminate()
            proc.wait()
        click.echo("Covalent server has stopped.")

    else:
        click.echo("Covalent server was not running.")

    _rm_pid_file(pidfile)


@click.command()
@click.option("-d", "--develop", is_flag=True, help="Start the server in developer mode.")
@click.option(
    "-p",
    "--port",
    default=get_config("user_interface.port"),
    show_default=True,
    help="Server port number.",
)
@click.option(
    "-m",
    "--mem-per-worker",
    required=False,
    is_flag=False,
    type=str,
    help="""Memory limit per worker in (GB).
              Provide strings like 1gb/1GB or 0 for no limits""".replace(
        "\n", ""
    ),
)
@click.option(
    "-n",
    "--workers",
    required=False,
    is_flag=False,
    type=int,
    help="Number of workers to start covalent with.",
)
@click.option(
    "-t",
    "--threads-per-worker",
    required=False,
    is_flag=False,
    type=int,
    help="Number of CPU threads per worker.",
)
@click.option(
    "--ignore-migrations",
    is_flag=True,
    required=False,
    show_default=True,
    default=False,
    help="Start the server without requiring migrations",
)
@click.option(
    "--no-cluster",
    is_flag=True,
    required=False,
    show_default=True,
    default=False,
    help="Start the server without Dask",
)
@click.pass_context
def start(
    ctx: click.Context,
    port: int,
    develop: bool,
    no_cluster: str,
    mem_per_worker: str,
    threads_per_worker: int,
    workers: int,
    ignore_migrations: bool,
) -> None:
    """
    Start the Covalent server.
    """
    if develop:
        set_config({"sdk.log_level": "debug"})

    db = DataStore.factory()

    # No migrations have run as of yet - run them automatically
    if not ignore_migrations and db.current_revision() is None:
        db.run_migrations(logging_enabled=False)

    if db.is_migration_pending and not ignore_migrations:
        click.secho(MIGRATION_WARNING_MSG, fg="yellow")
        click.echo(MIGRATION_COMMAND_MSG)
        return ctx.exit(1)

    if ignore_migrations and db.is_migration_pending:
        click.secho(
            'Warning: Ignoring migrations is not recommended and may have unanticipated side effects. Use "covalent db migrate" to run migrations.',
            fg="yellow",
        )

    set_config("user_interface.port", port)
    set_config("dispatcher.port", port)

    if not no_cluster:
        if mem_per_worker:
            set_config("dask.mem_per_worker", mem_per_worker)
        if threads_per_worker:
            set_config("dask.threads_per_worker", threads_per_worker)
        if workers:
            set_config("dask.num_workers", workers)

        set_config("sdk.no_cluster", "false")
    else:
        set_config("sdk.no_cluster", "true")

    port = _graceful_start(UI_SRVDIR, UI_PIDFILE, UI_LOGFILE, port, no_cluster, develop)
    set_config("user_interface.port", port)
    set_config("dispatcher.port", port)


@click.command()
def stop() -> None:
    """
    Stop the Covalent server.
    """
    _graceful_shutdown(UI_PIDFILE)


@click.command()
@click.option(
    "-p",
    "--port",
    default=None,
    type=int,
    help="Restart Covalent server on a different port.",
)
@click.option("-d", "--develop", is_flag=True, help="Start the server in developer mode.")
@click.pass_context
def restart(ctx, port: bool, develop: bool) -> None:
    """
    Restart the server.
    """

    no_cluster_map = {"true": True, "false": False}
    configuration = {
        "port": port or get_config("user_interface.port"),
        "develop": develop or (get_config("sdk.log_level") == "debug"),
        "no_cluster": no_cluster_map[get_config("sdk.no_cluster")],
        "mem_per_worker": get_config("dask.mem_per_worker"),
        "threads_per_worker": get_config("dask.threads_per_worker"),
        "workers": get_config("dask.num_workers"),
    }

    ctx.invoke(stop)
    ctx.invoke(start, **configuration)


@click.command()
def status() -> None:
    """
    Query the status of the Covalent server.
    """

    pid = _read_pid(UI_PIDFILE)
    if _read_pid(UI_PIDFILE) != -1 and psutil.pid_exists(pid):
        ui_port = get_config("user_interface.port")
        click.echo(f"Covalent server is running at http://localhost:{ui_port}.")
    else:
        _rm_pid_file(UI_PIDFILE)
        click.echo("Covalent server is stopped.")


@click.command()
@click.option(
    "-H",
    "--hard",
    is_flag=True,
    help="Perform a hard purge, deleting the DB as well. [default: False]",
)
@click.option(
    "-y", "--yes", is_flag=True, help="Approve without showing the warning. [default: False]"
)
@click.option("--hell-yeah", is_flag=True, hidden=True)
def purge(hard: bool, yes: bool, hell_yeah: bool) -> None:
    """
    Purge Covalent from this system. This command is for developers.
    """

    removal_list = {
        get_config("sdk.log_dir"),
        get_config("dispatcher.cache_dir"),
        get_config("dispatcher.log_dir"),
        get_config("user_interface.log_dir"),
        os.path.dirname(cm.config_file),
    }

    if hell_yeah:
        hard = True
        yes = True

    if hard:
        removal_list.add(get_config("dispatcher.db_path"))

    if not yes:

        click.secho(f"{''.join(['*'] * 21)} WARNING {''.join(['*'] * 21)}", fg="yellow")

        click.echo("Purging will perform the following operations: ")

        click.echo("1. Stop the covalent server if running.")

        for i, rem_path in enumerate(removal_list, start=2):
            if os.path.isdir(rem_path):
                click.echo(f"{i}. {rem_path} directory will be deleted.")
            else:
                click.echo(f"{i}. {rem_path} file will be deleted.")

        if hard:
            click.secho("WARNING: All user data will be deleted.", fg="red")

        click.confirm("\nWould you like to proceed?", abort=True)

    # Shutdown covalent server
    _graceful_shutdown(UI_PIDFILE)

    # Remove all directories and files
    for rem_path in removal_list:
        if os.path.isdir(rem_path):
            shutil.rmtree(rem_path, ignore_errors=True)
        else:
            with contextlib.suppress(FileNotFoundError):
                os.remove(rem_path)

        click.echo(f"Removed {rem_path}.")

    click.echo("Covalent server files have been purged.")


@click.command()
def logs() -> None:
    """
    Show Covalent server logs.
    """
    if os.path.exists(UI_LOGFILE):
        with open(UI_LOGFILE, "r") as logfile:
            for line in logfile:
                click.echo(line.rstrip("\n"))
    else:
        click.echo(f"{UI_LOGFILE} not found. Restart the server to create a new log file.")


@click.command()
@click.argument("result_pickle_path")
def migrate_legacy_result_object(result_pickle_path) -> None:
    """Migrate a legacy pickled Result object to the DataStore

    Example: `covalent migrate-legacy-result-object result.pkl`
    """

    migrate_pickled_result_object(result_pickle_path)


# Cluster CLI handlers (client side wrappers for the async handlers exposed
# in the dask cluster process)
async def _get_cluster_status(uri: str):
    """
    Returns status of all workers and scheduler in the cluster
    """
    async with rpc(uri, timeout=2) as r:
        cluster_status = await r.cluster_status()
    return cluster_status


async def _get_cluster_address(uri):
    """
    Returns the TCP addresses of the scheduler and workers
    """
    async with rpc(uri, timeout=2) as r:
        addresses = await r.cluster_address()
    return addresses


async def _get_cluster_info(uri):
    """
    Return summary of cluster info
    """
    async with rpc(uri, timeout=2) as r:
        return await r.cluster_info()


async def _cluster_restart(uri):
    """
    Restart the cluster by individually restarting the cluster workers
    """
    async with rpc(uri, timeout=2) as r:
        await r.cluster_restart()


async def _cluster_scale(uri: str, nworkers: int):
    """
    Scale the cluster up/down depending on `nworkers`
    """
    comm = await connect(uri, timeout=2)
    await comm.write({"op": "cluster_scale", "size": nworkers})
    result = await comm.read()
    comm.close()
    return result


async def _get_cluster_size(uri) -> int:
    async with rpc(uri, timeout=2) as r:
        size = await r.cluster_size()
    return size


async def _get_cluster_logs(uri):
    """
    Retrieve the cluster logs from the scheduler directly
    """
    comm = await connect(uri, timeout=2)
    await comm.write({"op": "cluster_logs"})
    cluster_logs = await comm.read()
    comm.close()
    return cluster_logs


@click.command()
@click.option("--status", is_flag=True, help="Show Dask cluster status")
@click.option("--info", is_flag=True, help="Retrieve Dask cluster info")
@click.option(
    "--address", is_flag=True, help="Fetch connection information of the cluster scheduler/workers"
)
@click.option("--size", is_flag=True, help="Return number of active workers in the cluster")
@click.option("--restart", is_flag=True, help="Restart the cluster")
@click.option(
    "--scale",
    is_flag=False,
    nargs=1,
    type=int,
    default=dask.system.CPU_COUNT,
    show_default=True,
    help="Scale cluster by adding/removing workers to match `nworkers`",
)
@click.option("--logs", is_flag=True, default=False, help="Show Dask cluster logs")
def cluster(
    status: bool, info: bool, address: bool, size: bool, restart: bool, scale: int, logs: bool
):
    """
    Inspect and manage the Dask cluster's configuration.
    """
    assert _is_server_running()
    # addr of the admin server for the Dask cluster process
    # started with covalent
    loop = asyncio.get_event_loop()
    admin_host = get_config("dask.admin_host")
    admin_port = get_config("dask.admin_port")
    admin_server_addr = unparse_address("tcp", f"{admin_host}:{admin_port}")

    if status:
        click.echo(
            json.dumps(
                loop.run_until_complete(_get_cluster_status(admin_server_addr)),
                sort_keys=True,
                indent=4,
            )
        )
        return
    if info:
        click.echo(
            json.dumps(
                loop.run_until_complete(_get_cluster_info(admin_server_addr)),
                sort_keys=True,
                indent=4,
            )
        )
        return
    if address:
        click.echo(
            json.dumps(
                loop.run_until_complete(_get_cluster_address(admin_server_addr)),
                sort_keys=True,
                indent=4,
            )
        )
        return
    if size:
        click.echo(
            json.dumps(
                loop.run_until_complete(_get_cluster_size(admin_server_addr)),
                sort_keys=True,
                indent=4,
            )
        )
        return
    if restart:
        loop.run_until_complete(_cluster_restart(admin_server_addr))
        click.echo("Cluster restarted")
        return
    if logs:
        click.echo(
            json.dumps(
                loop.run_until_complete(_get_cluster_logs(admin_server_addr)),
                sort_keys=True,
                indent=4,
            )
        )
        return
    if scale:
        loop.run_until_complete(_cluster_scale(admin_server_addr, nworkers=scale))
        click.echo(f"Cluster scaled to have {scale} workers")
        return


@click.command()
def config() -> None:
    """Print Covalent's configuration to stdout"""
    cm.read_config()
    click.echo(json.dumps(cm.config_data, sort_keys=True, indent=4))
