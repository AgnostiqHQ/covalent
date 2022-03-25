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


import contextlib
import os
import shutil
import socket
import time
from subprocess import DEVNULL, PIPE, Popen
from sys import stderr
from typing import Optional

import click
import psutil
import requests

from covalent._shared_files.config import _config_manager as cm
from covalent._shared_files.config import get_config, set_config

UI_PIDFILE = get_config("dispatcher.cache_dir") + "/ui.pid"
UI_LOGFILE = get_config("user_interface.log_dir") + "/covalent_ui.log"
UI_SRVDIR = os.path.dirname(os.path.abspath(__file__)) + "/../../covalent_ui"
SD_PIDFILE = f"{os.path.dirname(os.path.abspath(__file__))}/../../sd.pid"


def is_port_in_use(port: int, host: str = "localhost") -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) == 0


def _get_project_root_cwd() -> str:
    return f"{os.path.dirname(os.path.abspath(__file__))}/../../"


def _ensure_supervisord_running():
    cwd = _get_project_root_cwd()
    pid = _read_pid(SD_PIDFILE)
    if psutil.pid_exists(pid):
        click.echo(f"Supervisord already running in process {pid}.")
    else:
        proc = Popen(["supervisord"], stdout=DEVNULL, stderr=DEVNULL, cwd=cwd)
        pid = proc.pid
        with open(SD_PIDFILE, "w") as PIDFILE:
            PIDFILE.write(str(pid))
        count = 0
        while not is_port_in_use(9001):
            # if 30 seconds passes timeout
            if count > 300:
                click.echo("Supervisord was unable to start")
                break
            count += 1
            time.sleep(0.1)
        click.echo(f"Started Supervisord process {pid}.")


def _stop_services() -> None:
    _ensure_supervisord_running()
    cwd = _get_project_root_cwd()
    proc = Popen(["supervisorctl", "stop", "covalent:"], stdout=PIPE, cwd=cwd)
    while True:
        line = proc.stdout.readline()
        print(line.decode("utf-8").split("\n")[0])
        if not line:
            break


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


def _is_server_running(port: int) -> bool:
    """Check status of the Covalent server.

    Returns:
        status: Status of whether the server is running.
    """

    if _read_pid(UI_PIDFILE) == -1:
        return False
    try:
        r = requests.get(f"http://0.0.0.0:{port}")
    except:
        click.echo("Unable to connect to server.")
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
@click.pass_context
def start(ctx) -> None:
    cwd = _get_project_root_cwd()
    _ensure_supervisord_running()
    proc = Popen(["supervisorctl", "start", "covalent:"], stdout=PIPE, cwd=cwd)
    while True:
        line = proc.stdout.readline()
        click.echo(line.decode("utf-8").split("\n")[0])
        if not line:
            break


@click.command()
def status() -> None:
    _ensure_supervisord_running()
    cwd = _get_project_root_cwd()
    proc = Popen(["supervisorctl", "status"], stdout=PIPE, cwd=cwd)
    while True:
        line = proc.stdout.readline()
        click.echo(line.decode("utf-8").split("\n")[0])
        if not line:
            break


@click.command()
def stop() -> None:
    _stop_services()


@click.command()
def restart() -> None:
    _ensure_supervisord_running()
    cwd = _get_project_root_cwd()
    proc = Popen(["supervisorctl", "restart", "covalent:"], stdout=PIPE, cwd=cwd)
    while True:
        line = proc.stdout.readline()
        click.echo(line.decode("utf-8").split("\n")[0])
        if not line:
            break


@click.command()
@click.option(
    "-s",
    "--service",
    help="Service name",
)
@click.option(
    "-l",
    "--lines",
    default=1000,
    show_default=True,
    help="Lines (in bytes) to show for error logs",
)
def logs(service: str, lines: int) -> None:
    if not service:
        click.echo(
            "No service name provided, please use '-s <service_name>' or '--service <service_name>"
        )
        return
    _ensure_supervisord_running()
    cwd = _get_project_root_cwd()
    click.echo("_________________")
    click.echo(f"Errors last {lines} bytes:")
    click.echo("_________________")
    proc = Popen(
        [
            "supervisorctl",
            "tail",
            f"-{lines}",
            f"covalent:{service}",
            "stderr",
        ],
        stdout=PIPE,
        cwd=cwd,
    )

    while True:
        line = proc.stdout.readline()
        print(line.decode("utf-8").split("\n")[0])
        if not line:
            break
    click.echo("_________________")
    click.echo(f"Stdout last {lines} bytes:")
    click.echo("_________________")
    proc = Popen(
        ["supervisorctl", "tail", f"-{lines}", f"covalent:{service}"],
        stdout=PIPE,
        cwd=cwd,
    )

    while True:
        line = proc.stdout.readline()
        print(line.decode("utf-8").split("\n")[0])
        if not line:
            break
    click.echo("_________________")
    click.echo("Tailing current logs:")
    click.echo("_________________")
    proc = Popen(["supervisorctl", "tail", "-f", f"covalent:{service}"], stdout=PIPE, cwd=cwd)
    while True:
        line = proc.stdout.readline()
        print(line.decode("utf-8").split("\n")[0])
        if not line:
            break


@click.command()
def purge() -> None:
    """
    Shutdown server and delete the cache and config settings.
    """

    # Shutdown server.
    _stop_services()
    _graceful_shutdown(SD_PIDFILE)

    shutil.rmtree(get_config("sdk.log_dir"), ignore_errors=True)
    shutil.rmtree(get_config("dispatcher.cache_dir"), ignore_errors=True)
    shutil.rmtree(get_config("dispatcher.log_dir"), ignore_errors=True)
    shutil.rmtree(get_config("user_interface.log_dir"), ignore_errors=True)

    cm.purge_config()

    click.echo("Covalent server files have been purged.")
