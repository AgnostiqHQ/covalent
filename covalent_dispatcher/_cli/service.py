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

import os
import shutil
import socket
import time
from subprocess import DEVNULL, Popen
from typing import Optional

import click
import psutil

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
            sock.bind(("0.0.0.0", try_port))
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
        click.echo(f"Covalent server is already running at http://0.0.0.0:{port}.")
        return port

    _rm_pid_file(pidfile)

    pypath = f"PYTHONPATH={UI_SRVDIR}/../tests:$PYTHONPATH" if develop else ""
    dev_mode_flag = "--develop" if develop else ""
    port = _next_available_port(port)
    launch_str = f"{pypath} python app.py {dev_mode_flag} --port {port} >> {logfile} 2>&1"

    proc = Popen(launch_str, shell=True, stdout=DEVNULL, stderr=DEVNULL, cwd=server_root)
    pid = proc.pid

    with open(pidfile, "w") as PIDFILE:
        PIDFILE.write(str(pid))

    click.echo(f"Covalent server has started at http://0.0.0.0:{port}")
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
@click.option(
    "-p",
    "--port",
    default=get_config("user_interface.port"),
    show_default=True,
    help="Server port number.",
)
@click.option("-d", "--develop", is_flag=True, help="Start the server in developer mode.")
@click.pass_context
def start(ctx, port: int, develop: bool) -> None:
    """
    Start the Covalent server.
    """

    port = _graceful_start(UI_SRVDIR, UI_PIDFILE, UI_LOGFILE, port, develop)
    set_config(
        {
            "user_interface.address": "0.0.0.0",
            "user_interface.port": port,
            "dispatcher.address": "0.0.0.0",
            "dispatcher.port": port,
        }
    )

    # Wait until the server actually starts listening on the port
    server_listening = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while not server_listening:
        try:
            sock.bind(("0.0.0.0", port))
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

    if _read_pid(UI_PIDFILE) != -1:
        ui_port = get_config("user_interface.port")
        click.echo(f"Covalent server is running at http://0.0.0.0:{ui_port}.")
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
