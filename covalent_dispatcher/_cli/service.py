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
import os
import shutil
import socket
import sys
import time
from subprocess import DEVNULL, Popen
from typing import Optional

import click
import dask.system
import psutil
from distributed.comm import unparse_address
from distributed.core import connect, rpc

from covalent._shared_files.config import _config_manager as cm
from covalent._shared_files.config import get_config, set_config

UI_PIDFILE = get_config("dispatcher.cache_dir") + "/ui.pid"
UI_LOGFILE = get_config("user_interface.log_dir") + "/covalent_ui.log"
UI_SRVDIR = os.path.dirname(os.path.abspath(__file__)) + "/../../covalent_ui"


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
    if _read_pid(UI_PIDFILE) == -1:
        return False
    return True


def _graceful_start(
    server_root: str,
    pidfile: str,
    logfile: str,
    port: int,
    no_cluster: str,
    develop: bool = False,
) -> int:
    """
    Gracefully start a Flask app.

    Args:
        server_root: Directory where app.py is located.
        pidfile: Process ID file for the server.
        logfile: Log file for the server.
        port: Port requested to be used by the server.
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
    no_cluster_flag = "--no-cluster"
    port = _next_available_port(port)
    if no_cluster_flag in sys.argv:
        launch_str = f"{pypath} python app.py {dev_mode_flag} --port {port} --no-cluster {no_cluster} >> {logfile} 2>&1"
    else:
        launch_str = f"{pypath} python app.py {dev_mode_flag} --port {port} >> {logfile} 2>&1"

    proc = Popen(launch_str, shell=True, stdout=DEVNULL, stderr=DEVNULL, cwd=server_root)
    pid = proc.pid

    with open(pidfile, "w") as PIDFILE:
        PIDFILE.write(str(pid))

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
        try:
            child_proc.kill()
            child_proc.wait()
        except psutil.NoSuchProcess:
            pass


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

        try:
            proc.terminate()
            proc.wait()
        except psutil.NoSuchProcess:
            pass

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
    default="auto",
    show_default=True,
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
    default=dask.system.CPU_COUNT,
    show_default=True,
    type=int,
    help="Number of workers to start covalent with.",
)
@click.option(
    "-t",
    "--threads-per-worker",
    required=False,
    is_flag=False,
    default=1,
    show_default=True,
    type=int,
    help="Number of CPU threads per worker.",
)
@click.option(
    "--no-cluster",
    is_flag=True,
    required=False,
    show_default=True,
    default=False,
    help="Start the server without Dask",
)
@click.argument("no-cluster", required=False)
@click.pass_context
def start(
    ctx,
    port: int,
    develop: bool,
    no_cluster: str,
    mem_per_worker: int,
    threads_per_worker: int,
    workers: int,
) -> None:
    """
    Start the Covalent server.
    """
    port = _graceful_start(UI_SRVDIR, UI_PIDFILE, UI_LOGFILE, port, no_cluster, develop)
    no_cluster_flag = "--no-cluster"
    set_config(
        {
            "user_interface.address": "localhost",
            "user_interface.port": port,
            "dispatcher.address": "localhost",
            "dispatcher.port": port,
            "dask": {
                "mem_per_worker": mem_per_worker or "auto",
                "threads_per_worker": threads_per_worker or 1,
                "num_workers": workers or dask.system.CPU_COUNT,
            },
        }
    )

    # Wait until the server actually starts listening on the port
    server_listening = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while not server_listening:
        try:
            sock.bind(("localhost", port))
            sock.close()
        except OSError:
            server_listening = True

        time.sleep(1)


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
    port = port or get_config("user_interface.port")

    ctx.invoke(stop)
    ctx.invoke(start, port=port, develop=develop)


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
def purge() -> None:
    """
    Shutdown server and delete the cache and config settings.
    """

    # Shutdown server.
    _graceful_shutdown(UI_PIDFILE)

    shutil.rmtree(get_config("sdk.log_dir"), ignore_errors=True)
    shutil.rmtree(get_config("dispatcher.cache_dir"), ignore_errors=True)
    shutil.rmtree(get_config("dispatcher.log_dir"), ignore_errors=True)
    shutil.rmtree(get_config("user_interface.log_dir"), ignore_errors=True)

    cm.purge_config()

    click.echo("Covalent server files have been purged.")


@click.command()
def logs() -> None:
    """
    Show Covalent server logs.
    """
    if os.path.exists(UI_LOGFILE):
        f = open(UI_LOGFILE, "r")
        line = f.readline()
        while line:
            click.echo(line.rstrip("\n"))
            line = f.readline()
        f.close()
    else:
        click.echo(f"{UI_LOGFILE} not found!. Server possibly purged!")


# Cluster CLI handlers (client side wrappers for the async handlers exposed
# in the dask cluster process)
async def _get_cluster_status(uri: str):
    """
    Returns status of all workers and scheduler in the cluster
    """
    async with rpc(uri) as r:
        cluster_status = await r.cluster_status()
    return cluster_status


async def _get_cluster_address(uri):
    """
    Returns the TCP addresses of the scheduler and workers
    """
    async with rpc(uri) as r:
        addresses = await r.cluster_address()
    return addresses


async def _get_cluster_info(uri):
    """
    Return summary of cluster info
    """
    async with rpc(uri) as r:
        return await r.cluster_info()


async def _cluster_restart(uri):
    """
    Restart the cluster by individually restarting the cluster workers
    """
    async with rpc(uri) as r:
        await r.cluster_restart()


async def _cluster_scale(uri: str, nworkers: int):
    """
    Scale the cluster up/down depending on `nworkers`
    """
    comm = await connect(uri)
    await comm.write({"op": "cluster_scale", "size": nworkers})
    result = await comm.read()
    comm.close()
    return result


async def _get_cluster_size(uri) -> int:
    async with rpc(uri) as r:
        size = await r.cluster_size()
    return size


async def _get_cluster_logs(uri):
    """
    Retrive the cluster logs from the scheduler directly
    """
    click.echo("Calling logs handler")
    comm = await connect(uri)
    await comm.write({"op": "cluster_logs"})
    cluster_logs = await comm.read()
    comm.close()
    return cluster_logs


@click.command()
@click.option("--status", is_flag=True, help="Show Dask cluster status")
@click.option("--info", is_flag=True, help="Retrive Dask cluster info")
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
    # addr of the admin server for the Dask cluster process
    # started with covalent
    loop = asyncio.get_event_loop()
    try:
        admin_host = get_config("dask.admin_host")
        admin_port = get_config("dask.admin_port")
        admin_server_addr = unparse_address("tcp", f"{admin_host}:{admin_port}")

        if status:
            click.echo(loop.run_until_complete(_get_cluster_status(admin_server_addr)))
            return

        if info:
            click.echo(loop.run_until_complete(_get_cluster_info(admin_server_addr)))
            return

        if address:
            click.echo(loop.run_until_complete(_get_cluster_address(admin_server_addr)))
            return

        if size:
            click.echo(loop.run_until_complete(_get_cluster_size(admin_server_addr)))
            return

        if restart:
            loop.run_until_complete(_cluster_restart(admin_server_addr))
            click.echo("Cluster restarted")
            return

        if logs:
            click.echo(loop.run_until_complete(_get_cluster_logs(admin_server_addr)))
            return

        if scale:
            loop.run_until_complete(_cluster_scale(admin_server_addr, nworkers=scale))
            click.echo(f"Cluster scaled to have {scale} workers")
            return
    except KeyError:
        click.echo("Error")
