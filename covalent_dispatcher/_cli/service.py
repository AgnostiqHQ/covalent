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
from subprocess import DEVNULL, PIPE, Popen
from sys import stderr
from typing import Optional

import click
import psutil
import requests
from dotenv import dotenv_values
from jinja2 import Template

from covalent._shared_files.config import _config_manager as cm
from covalent._shared_files.config import get_config, set_config

SUPERVISORD_PORT = 9001
UI_PIDFILE = get_config("dispatcher.cache_dir") + "/ui.pid"
UI_LOGFILE = get_config("user_interface.log_dir") + "/covalent_ui.log"
UI_SRVDIR = os.path.dirname(os.path.abspath(__file__)) + "/../../covalent_ui"
SD_PIDFILE = os.path.dirname(os.path.abspath(__file__)) + "/../../supervisord.pid"
SD_CONFIG_FILE = os.path.dirname(os.path.abspath(__file__)) + "/../../supervisord.conf"

SD_START_TIMEOUT_IN_SECS = 15


def _read_process_stdout(proc):
    while True:
        line = proc.stdout.readline()
        click.echo(line.decode("utf-8").split("\n")[0])
        if not line:
            break


def _is_port_in_use(port: int, host: str = "localhost") -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) == 0


def _get_project_root_cwd() -> str:
    return os.path.dirname(os.path.abspath(__file__)) + "/../../"


def _generate_supervisord_config():
    project_root_path = os.path.dirname(os.path.abspath(__file__)) + "/../.."
    # TODO consider using an external .env file for configuring defaults
    # print({
    #     **dotenv_values(f"{project_root_path}/.env")
    # })
    with open(
        f"{project_root_path}/covalent_dispatcher/_cli/supervisord.template.conf", "r"
    ) as file:
        template = file.read()
        j2_template = Template(template)
        config = j2_template.render(
            {
                "project_root": project_root_path,
                "queuer_svc_port": "8001",
                "dispatcher_svc_port": "8002",
                "runner_svc_port": "8003",
                "data_svc_port": "8004",
                "ui_backend_svc_port": "8005",
                "results_svc_port": "8006",
                "mq_connection_uri": "localhost:4222",
                "mq_dispatch_topic": "workflow.dispatch",
                "sd_dashboard_port": str(SUPERVISORD_PORT),
                "sd_pid_file_path": SD_PIDFILE,
            }
        )
        return config


def _create_config_if_not_exists() -> str:
    config_file_content = _generate_supervisord_config()
    exists = False
    try:
        open(SD_CONFIG_FILE, "r").readline()
        exists = True
    except FileNotFoundError:
        exists = False
    if not exists:
        with open(SD_CONFIG_FILE, "w") as config_file:
            config_file.write(config_file_content)
    return config_file_content


def _is_supervisord_running() -> bool:
    pid = _read_pid(SD_PIDFILE)
    return psutil.pid_exists(pid)


def _ensure_supervisord_running():
    _create_config_if_not_exists()
    cwd = _get_project_root_cwd()
    if _is_supervisord_running():
        pid = _read_pid(SD_PIDFILE)
        click.echo(f"Supervisord already running in process {pid}.")
    else:
        Popen(["supervisord"], stdout=DEVNULL, stderr=DEVNULL, cwd=cwd)
        count = 0
        wait_interval_in_secs = 0.1
        while not _is_port_in_use(SUPERVISORD_PORT):
            # if 15 seconds passes timeout
            if count > (SD_START_TIMEOUT_IN_SECS / wait_interval_in_secs):
                raise click.ClickException("Supervisord was unable to start")
            elif count == 2:
                click.echo("Checking if covalent has started (this may take a few seconds)...")
            count += 1
            time.sleep(wait_interval_in_secs)
        # get new pid as a result of starting supervisord
        pid = _read_pid(SD_PIDFILE)
        click.echo(f"Started Supervisord process {pid}.")


def _sd_status() -> None:
    _ensure_supervisord_running()
    cwd = _get_project_root_cwd()
    proc = Popen(["supervisorctl", "status"], stdout=PIPE, cwd=cwd)
    _read_process_stdout(proc)


def _sd_restart_services() -> None:
    _ensure_supervisord_running()
    cwd = _get_project_root_cwd()
    proc = Popen(["supervisorctl", "restart", "covalent:"], stdout=PIPE, cwd=cwd)
    _read_process_stdout(proc)


def _sd_start_services() -> None:
    cwd = _get_project_root_cwd()
    _ensure_supervisord_running()
    proc = Popen(["supervisorctl", "start", "covalent:"], stdout=PIPE, cwd=cwd)
    _read_process_stdout(proc)


def _sd_stop_services() -> None:
    _ensure_supervisord_running()
    cwd = _get_project_root_cwd()
    proc = Popen(["supervisorctl", "stop", "covalent:"], stdout=PIPE, cwd=cwd)
    _read_process_stdout(proc)


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
@click.option("--refactor", is_flag=True, help="Use post refactor cli command [with Supervisord]")
@click.option(
    "-p",
    "--port",
    default=get_config("user_interface.port"),
    show_default=True,
    type=int,
    help="Server port number.",
)
@click.option("-d", "--develop", is_flag=True, help="Start the server in developer mode.")
def start(refactor, port: int, develop: bool) -> None:
    if refactor:
        _sd_start_services()
    else:
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
@click.option("--refactor", is_flag=True, help="Use post refactor cli command [with Supervisord]")
def status(refactor) -> None:
    if refactor:
        _sd_status()
    else:
        if _read_pid(UI_PIDFILE) != -1:
            ui_port = get_config("user_interface.port")
            click.echo(f"Covalent server is running at http://0.0.0.0:{ui_port}.")
        else:
            _rm_pid_file(UI_PIDFILE)
            click.echo("Covalent server is stopped.")


@click.command()
@click.option("--refactor", is_flag=True, help="Use post refactor cli command [with Supervisord]")
def stop(refactor) -> None:
    if refactor:
        _sd_stop_services()
    else:
        _graceful_shutdown(UI_PIDFILE)


@click.command()
def config() -> None:
    config_file_content = _create_config_if_not_exists()
    click.echo(config_file_content)


@click.command()
@click.option(
    "-p",
    "--port",
    default=None,
    type=int,
    help="Restart Covalent server on a different port.",
)
@click.option("-d", "--develop", is_flag=True, help="Start the server in developer mode.")
@click.option("--refactor", is_flag=True, help="Use post refactor cli command [with Supervisord]")
@click.pass_context
def restart(ctx, port: int, develop: bool, refactor: bool) -> None:
    """
    Restart the server(s).
    """
    if refactor:
        _sd_restart_services()
    else:
        port = port or get_config("user_interface.port")
        ctx.invoke(stop)
        ctx.invoke(start, port=port, develop=develop)


@click.command()
@click.option(
    "-p",
    "--port",
    default=get_config("user_interface.port"),
    show_default=True,
    type=int,
    help="Check server status on a specific port.",
)
@click.option("-d", "--develop", is_flag=True, help="Start the server in developer mode.")
@click.option("--refactor", is_flag=True, help="Use post refactor cli command [with Supervisord]")
@click.pass_context
def status(ctx, port: int, develop: bool, refactor: bool) -> None:
    """
    Query the status of the Covalent server.
    """
    if refactor:
        _sd_status()
    else:
        if port and _is_server_running(port):
            click.echo(f"Covalent server is running at http://0.0.0.0:{port}.")
        else:
            _rm_pid_file(UI_PIDFILE)
            click.echo("Covalent server is stopped.")


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
    click.echo(f"Errors last {str(lines)} bytes:")
    click.echo("_________________")
    proc = Popen(
        ["supervisorctl", "tail", f"-{str(lines)}", f"covalent:{service}", "stderr"],
        stdout=PIPE,
        cwd=cwd,
    )
    _read_process_stdout(proc)
    click.echo("_________________")
    click.echo(f"Stdout last {str(lines)} bytes:")
    click.echo("_________________")
    proc = Popen(
        ["supervisorctl", "tail", f"-{str(lines)}", f"covalent:{service}"], stdout=PIPE, cwd=cwd
    )
    _read_process_stdout(proc)
    click.echo("_________________")
    click.echo("Tailing current logs:")
    click.echo("_________________")
    proc = Popen(["supervisorctl", "tail", "-f", f"covalent:{service}"], stdout=PIPE, cwd=cwd)
    _read_process_stdout(proc)


@click.command()
@click.option("--refactor", is_flag=True, help="Use post refactor cli command [with Supervisord]")
def purge(refactor) -> None:
    """
    Shutdown server and delete the cache and config settings.
    """

    # Shutdown servers and supervisord
    if refactor and _is_supervisord_running():
        _sd_stop_services()
        _graceful_shutdown(SD_PIDFILE)

    if os.path.exists(SD_CONFIG_FILE):
        os.remove(SD_CONFIG_FILE)

    # Shutdown legacy server
    if not refactor:
        _graceful_shutdown(UI_PIDFILE)

    shutil.rmtree(get_config("sdk.log_dir"), ignore_errors=True)
    shutil.rmtree(get_config("dispatcher.cache_dir"), ignore_errors=True)
    shutil.rmtree(get_config("dispatcher.log_dir"), ignore_errors=True)
    shutil.rmtree(get_config("user_interface.log_dir"), ignore_errors=True)

    cm.purge_config()

    click.echo("Covalent server files have been purged.")
