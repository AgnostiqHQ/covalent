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
import signal
import socket
from subprocess import Popen

import click
import psutil

from covalent._shared_files.config import _config_manager as cm
from covalent._shared_files.config import get_config, set_config

DISPATCHER_PIDFILE = get_config("dispatcher.cache_dir") + "/dispatcher.pid"
DISPATCHER_LOGFILE = get_config("dispatcher.log_dir") + "/dispatcher.log"
DISPATCHER_SRVDIR = os.path.dirname(os.path.abspath(__file__)) + "/../_service"

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


def _port_from_pid(pid: int) -> int:
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


def _is_dispatcher_running() -> bool:
    """Check status of dispatcher server.

    Returns:
        status: Status of whether the dispatcher server is running.
    """

    if _read_pid(DISPATCHER_PIDFILE) == -1:
        return False
    return True


def _is_ui_running() -> bool:
    """Check status of user interface (UI) server.

    Returns:
        status: Status of whether the user interface server is running.
    """

    if _read_pid(UI_PIDFILE) == -1:
        return False
    return True


def _graceful_start(
    server_name: str,
    server_root: str,
    pidfile: str,
    logfile: str,
    port: int,
    develop: bool = False,
) -> int:
    """
    Gracefully start a Flask app with gunicorn.

    Args:
        server_name: Name of the server. 'dispatcher' or 'UI'.
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
        port = _port_from_pid(pid)
        click.echo(f"Covalent {server_name} server is already running at http://0.0.0.0:{port}.")
        return port

    _rm_pid_file(pidfile)

    port = _next_available_port(port)

    reload = "--reload" if develop else ""
    eventlet = "--worker-class eventlet" if server_name == "UI" else ""
    pythonpath = (
        f'--pythonpath="{server_root}/../../tests/functional_tests"'
        if develop and server_name == "dispatcher"
        else ""
    )

    launch_str = f"gunicorn -w 1 -t 30 -b 0.0.0.0:{port} {eventlet} --daemon --chdir {server_root} --pid {pidfile} --capture-output --log-file {logfile} {reload} {pythonpath} --reuse-port app:app"

    proc = Popen(
        launch_str,
        shell=True,
    )

    click.echo(f"Covalent {server_name} server has started at http://0.0.0.0:{port}")

    return port


def _graceful_shutdown(server_name: str, pidfile: str) -> None:
    """
    Gracefully shut down a server given a process ID.

    Args:
        server_name: Name of the server.
        pidfile: Process ID file for the server.

    Returns:
        None
    """

    pid = _read_pid(pidfile)
    if psutil.pid_exists(pid):
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait()
        click.echo(f"Covalent {server_name} server has stopped.")
    else:
        click.echo(f"Covalent {server_name} server was not running.")
    _rm_pid_file(pidfile)


def _graceful_restart(server_name: str, pidfile: str) -> bool:
    """Gracefully restart a server given a process ID."""

    pid = _read_pid(pidfile)
    if pid != -1:
        os.kill(pid, signal.SIGHUP)
        click.echo(
            f"Covalent {server_name} server has restarted on port http://0.0.0.0:{_port_from_pid(pid)}."
        )
        return True
    else:
        return False


@click.command()
@click.option(
    "--dispatcher",
    is_flag=True,
    help="Start only the dispatcher server.",
)
@click.option(
    "--ui",
    is_flag=True,
    help="Start only the UI server.",
)
@click.option(
    "-p",
    "--port",
    default=get_config("dispatcher.port"),
    show_default=True,
    help="Local dispatcher server port number.",
)
@click.option(
    "-P",
    "--ui-port",
    default=get_config("user_interface.port"),
    show_default=True,
    help="Local user interface server port number.",
)
@click.option("-d", "--develop", is_flag=True, help="Start the server(s) in developer mode.")
def start(dispatcher: bool, ui: bool, port: int, ui_port: int, develop: bool) -> None:
    """
    Start the dispatcher and/or UI servers.
    """

    if not (dispatcher or ui):
        dispatcher = True
        ui = True

    if dispatcher:
        port = _graceful_start(
            "dispatcher", DISPATCHER_SRVDIR, DISPATCHER_PIDFILE, DISPATCHER_LOGFILE, port, develop
        )
        set_config(
            {
                "dispatcher.address": "0.0.0.0",
                "dispatcher.port": port,
            }
        )

    if ui:
        ui_port = _graceful_start("UI", UI_SRVDIR, UI_PIDFILE, UI_LOGFILE, ui_port, develop)
        set_config(
            {
                "user_interface.address": "0.0.0.0",
                "user_interface.port": ui_port,
            }
        )


@click.command()
@click.option(
    "--dispatcher",
    is_flag=True,
    help="Stop only the dispatcher server.",
)
@click.option(
    "--ui",
    is_flag=True,
    help="Stop only the UI server.",
)
def stop(dispatcher: bool, ui: bool) -> None:
    """
    Stop the dispatcher and/or UI servers.
    """

    if not (dispatcher or ui):
        dispatcher = True
        ui = True

    if dispatcher:
        _graceful_shutdown("dispatcher", DISPATCHER_PIDFILE)

    if ui:
        _graceful_shutdown("UI", UI_PIDFILE)


@click.command()
@click.option(
    "--dispatcher",
    is_flag=True,
    help="Restart only the dispatcher server.",
)
@click.option(
    "--ui",
    is_flag=True,
    help="Restart only the UI server.",
)
@click.option(
    "-p", "--port", default=None, type=int, help="Restart dispatcher server on a different port."
)
@click.option(
    "-P",
    "--ui-port",
    default=None,
    type=int,
    help="Restart UI server on a different port.",
)
@click.option("-d", "--develop", is_flag=True, help="Start the server(s) in developer mode.")
@click.pass_context
def restart(ctx, dispatcher: bool, ui: bool, port: int, ui_port: int, develop: bool) -> None:
    """
    Restart the dispatcher and/or UI servers.
    """

    if not (dispatcher or ui):
        dispatcher = True
        ui = True

    if dispatcher:
        pid = _read_pid(DISPATCHER_PIDFILE)
        port = port or _port_from_pid(pid) or get_config("dispatcher.port")
        if pid == -1 or port != get_config("dispatcher.port") or develop:
            ctx.invoke(stop, dispatcher=True)
            ctx.invoke(start, dispatcher=True, port=port, develop=develop)
        elif pid != -1:
            started = _graceful_restart("dispatcher", DISPATCHER_PIDFILE)
            if not started:
                ctx.invoke(start, dispatcher=True, port=port, develop=develop)

    if ui:
        pid = _read_pid(UI_PIDFILE)
        port = ui_port or _port_from_pid(pid) or get_config("user_interface.port")
        if pid == -1 or port != get_config("user_interface.port") or develop:
            ctx.invoke(stop, ui=True)
            ctx.invoke(start, ui=True, ui_port=port, develop=develop)
        elif pid != -1:
            started = _graceful_restart("user interface", UI_PIDFILE)
            if not started:
                ctx.invoke(start, ui=True, ui_port=port, develop=develop)


@click.command()
def status() -> None:
    """
    Query the status of the dispatcher and UI servers.
    """

    dispatcher_port = _port_from_pid(_read_pid(DISPATCHER_PIDFILE))
    if dispatcher_port is not None:
        click.echo(f"Covalent dispatcher server is running at http://0.0.0.0:{dispatcher_port}.")
    else:
        _rm_pid_file(DISPATCHER_PIDFILE)
        click.echo("Covalent dispatcher server is stopped.")

    ui_port = _port_from_pid(_read_pid(UI_PIDFILE))
    if ui_port is not None:
        click.echo(f"Covalent UI server is running at http://0.0.0.0:{ui_port}.")
    else:
        _rm_pid_file(UI_PIDFILE)
        click.echo("Covalent UI server is stopped.")


@click.command()
def purge() -> None:
    """
    Shutdown servers and delete the cache and config settings.
    """

    # Shutdown UI and dispatcher server.
    _graceful_shutdown("dispatcher", DISPATCHER_PIDFILE)
    _graceful_shutdown("UI", UI_PIDFILE)

    shutil.rmtree(get_config("sdk.log_dir"), ignore_errors=True)
    shutil.rmtree(get_config("dispatcher.cache_dir"), ignore_errors=True)
    shutil.rmtree(get_config("dispatcher.log_dir"), ignore_errors=True)
    shutil.rmtree(get_config("user_interface.log_dir"), ignore_errors=True)

    cm.purge_config()

    click.echo("Covalent server files have been purged.")
