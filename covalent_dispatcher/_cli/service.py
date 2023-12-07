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

"""Covalent CLI Tool - Service Management."""


import asyncio
import contextlib
import json
import os
import shutil
import signal
import socket
import sys
import time
import traceback
from pathlib import Path
from subprocess import DEVNULL, Popen
from typing import Optional

import click
import dask.system
import psutil
import requests
import sqlalchemy
from dask.distributed import Client
from distributed.comm import unparse_address
from distributed.comm.core import CommClosedError
from distributed.core import connect, rpc
from furl import furl
from natsort import natsorted
from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.status import Status
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from covalent._shared_files.config import ConfigManager, get_config, reload_config, set_config

from .._db.datastore import DataStore
from .migrate import migrate_pickled_result_object

UI_PIDFILE = get_config("dispatcher.cache_dir") + "/ui.pid"
UI_LOGFILE = get_config("user_interface.log_dir") + "/covalent_ui.log"
UI_SRVDIR = f"{os.path.dirname(os.path.abspath(__file__))}/../../covalent_ui"

MIGRATION_WARNING_MSG = "Covalent not started. The database needs to be upgraded."
MIGRATION_COMMAND_MSG = (
    '   (use "covalent db migrate" to run database migrations and then retry "covalent start")'
)
ZOMBIE_PROCESS_STATUS_MSG = "Covalent server is unhealthy: Process is in zombie status"
STOPPED_PROCESS_STATUS_MSG = "Covalent server is unhealthy: Process is in stopped status"


def print_header(console):
    branding_title = Text("Covalent", style="bold blue")
    github_link = Text("GitHub: https://github.com/AgnostiqHQ/covalent", style="cyan")
    docs_link = Text("Docs:   https://docs.covalent.xyz", style="cyan")
    console.print(Panel.fit(branding_title, padding=(1, 20)))
    console.print(github_link)
    console.print(docs_link)
    console.print()


def print_footer(console):
    console.print("\nFor additional help, use 'covalent --help'")


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
    no_triggers: bool = False,
    triggers_only: bool = False,
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
        no_triggers: Start the server without Triggers endpoints.
        triggers_only: Start the server with only Triggers endpoints.

    Returns:
        port: Port assigned to the server.
    """

    pid = _read_pid(pidfile)
    if psutil.pid_exists(pid):
        port = get_config("dispatcher.port")
        return port

    _rm_pid_file(pidfile)

    if no_triggers and triggers_only:
        raise ValueError(
            "Options '--no-triggers' and '--triggers-only' are mutually exclusive, please choose one at most."
        )

    no_triggers_flag = "--no-triggers" if no_triggers else ""
    triggers_only_flag = "--triggers-only" if triggers_only else ""

    pypath = f"PYTHONPATH={UI_SRVDIR}/../tests:$PYTHONPATH" if develop else ""
    dev_mode_flag = "--develop" if develop else ""
    no_cluster_flag = "--no-cluster" if no_cluster else ""

    port = _next_available_port(port)
    launch_str = f"{pypath} {sys.executable} app.py {dev_mode_flag} --port {port} {no_cluster_flag} {no_triggers_flag} {triggers_only_flag}>> {logfile} 2>&1"

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
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    # Since the dispatcher process might update the config file with the Dask cluster's state,
    # we need to sync those changes with the CLI's ConfigManager instance. Otherwise the next
    # call to `set_config()` from this module would obliterate the Dask cluster state.
    reload_config()

    Path(get_config("dispatcher.cache_dir")).mkdir(parents=True, exist_ok=True)
    Path(get_config("dispatcher.results_dir")).mkdir(parents=True, exist_ok=True)
    Path(get_config("dispatcher.log_dir")).mkdir(parents=True, exist_ok=True)
    Path(get_config("user_interface.log_dir")).mkdir(parents=True, exist_ok=True)

    return port


def _terminate_child_processes(pid: int) -> None:
    """For a given process, find all the child processes and terminate them.

    Args:
        pid: Process ID file for the main server process.

    Returns:
        None
    """

    # Uvicorn
    leader = psutil.Process(pid).children()[0]

    # Dask
    children = psutil.Process(leader.pid).children(recursive=True)

    with contextlib.suppress(psutil.NoSuchProcess):
        leader.send_signal(signal.SIGINT)

    for child_proc in children:
        with contextlib.suppress(psutil.NoSuchProcess):
            child_proc.kill()

    psutil.wait_procs(children)
    leader.wait()


def _graceful_shutdown(pidfile: str) -> None:
    """
    Gracefully shut down a server given a process ID.

    Args:
        pidfile: Process ID file for the server.

    Returns:
        None
    """
    console = Console()
    pid = _read_pid(pidfile)
    if psutil.pid_exists(pid):
        proc = psutil.Process(pid)
        _terminate_child_processes(pid)

        with contextlib.suppress(psutil.NoSuchProcess):
            proc.terminate()
            proc.wait()

    else:
        console.print("[yellow]Covalent server was not running.[/yellow]\n")

    _rm_pid_file(pidfile)


@click.command()
@click.option("-d", "--develop", is_flag=True, help="Start local server in developer mode")
@click.option(
    "-p",
    "--port",
    default=get_config("dispatcher.port"),
    show_default=True,
    help="Local server port number",
)
@click.option(
    "-m",
    "--mem-per-worker",
    required=False,
    is_flag=False,
    type=str,
    help="""Memory limit per worker in GB.
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
    help="Number of Dask workers",
)
@click.option(
    "-t",
    "--threads-per-worker",
    required=False,
    is_flag=False,
    type=int,
    help="Number of threads per Dask worker",
)
@click.option(
    "--ignore-migrations",
    is_flag=True,
    required=False,
    show_default=True,
    default=False,
    help="Start server without database migrations",
)
@click.option(
    "--no-cluster",
    is_flag=True,
    required=False,
    show_default=True,
    default=False,
    help="Start server without Dask cluster",
)
@click.option(
    "--no-triggers",
    is_flag=True,
    required=False,
    show_default=True,
    default=False,
    help="Start server without a triggers server",
)
@click.option(
    "--triggers-only",
    is_flag=True,
    required=False,
    show_default=True,
    default=False,
    help="Start only the triggers server",
)
@click.option("--no-header", is_flag=True, default=False, hidden=True)
@click.option("--no-footer", is_flag=True, default=False, hidden=True)
@click.pass_context
def start(
    ctx: click.Context,
    port: int,
    develop: bool,
    no_cluster: bool,
    mem_per_worker: str,
    threads_per_worker: int,
    workers: int,
    ignore_migrations: bool,
    no_triggers: bool,
    triggers_only: bool,
    no_header: bool,
    no_footer: bool,
) -> None:
    """
    Start a local server
    """

    console = Console()

    if not no_header:
        print_header(console)

    # Display a header with a border
    console.print(Panel("Starting Local Server", expand=False, border_style="blue"))
    console.print()

    if os.environ.get("COVALENT_DEBUG_MODE") == "1":
        develop = True

    if os.environ.get("COVALENT_DISABLE_DASK") == "1":
        no_cluster = True

    if develop:
        set_config({"sdk.log_level": "debug"})

    db = DataStore.factory()

    # No migrations have run as of yet - run them automatically
    if not ignore_migrations and db.current_revision() is None:
        with Status("Running migrations...", console=console):
            db.run_migrations(logging_enabled=False)

    if db.is_migration_pending and not ignore_migrations:
        console.print(MIGRATION_WARNING_MSG, style="yellow")
        console.print(MIGRATION_COMMAND_MSG)
        console.print()
        return ctx.exit(1)

    if ignore_migrations and db.is_migration_pending:
        console.print(
            'Warning: Ignoring migrations is not recommended and may have unanticipated side effects. Use "covalent db migrate" to run migrations.',
            style="yellow",
        )
        console.print()

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

    try:
        with Status("Starting server...", console=console):
            port = _graceful_start(
                UI_SRVDIR,
                UI_PIDFILE,
                UI_LOGFILE,
                port,
                no_cluster,
                develop,
                no_triggers,
                triggers_only,
            )
    except Exception:
        click.secho("Error: ", fg="red")
        click.secho(
            "Covalent was unable to start due to the following error: ", fg="red", bold=True
        )
        click.secho(traceback.format_exc(), fg="lightgrey")

    set_config("user_interface.port", port)
    set_config("dispatcher.port", port)

    # Display server configuration in a table
    config_table = Table(title="Covalent Server Configuration", box=ROUNDED, show_header=False)
    config_table.add_column("Option", style="bold", no_wrap=True)
    config_table.add_column("Value")

    config_table.add_row(
        "Dispatcher Address", Text(str(get_config("dispatcher.address")), style="green")
    )
    config_table.add_row("Port", Text(str(port), style="green"))
    config_table.add_row("Develop", Text(str(develop), style="blue" if develop else "green"))
    config_table.add_row(
        "Disable Dask", Text(str(no_cluster), style="blue" if no_cluster else "green")
    )
    config_table.add_row("Memory per Worker", Text(str(mem_per_worker), style="magenta"))
    config_table.add_row("Threads per Worker", Text(str(threads_per_worker), style="magenta"))
    config_table.add_row("Workers", Text(str(workers), style="magenta"))
    config_table.add_row(
        "Ignore Migrations",
        Text(str(ignore_migrations), style="yellow" if ignore_migrations else "green"),
    )
    config_table.add_row(
        "Disable Triggers", Text(str(no_triggers), style="blue" if no_triggers else "green")
    )
    config_table.add_row(
        "Triggers Only", Text(str(triggers_only), style="blue" if triggers_only else "green")
    )

    console.print(config_table)
    console.print("\nServer Status: [green]:heavy_check_mark:[/green] Running", style="bold")

    dispatcher_address = f"http://{str(get_config('dispatcher.address'))}:{str(port)}"
    console.print(f"\nCovalent UI can be accessed at {dispatcher_address}")

    if not no_footer:
        console.print("\nFor a summary of the system status, use 'covalent status'")
        print_footer(console)


@click.command()
@click.option("--no-header", is_flag=True, default=False, hidden=True)
@click.option("--no-footer", is_flag=True, default=False, hidden=True)
def stop(no_header: bool, no_footer: bool) -> None:
    """
    Stop a local server
    """

    console = Console()
    if not no_header:
        print_header(console)

    console.print(Panel("Stopping Local Server", expand=False, border_style="blue"))
    console.print()

    with Status("Stopping server...", console=console):
        _graceful_shutdown(UI_PIDFILE)

    console.print("Server status: [red]:heavy_multiplication_x:[/red] Stopped", style="bold")

    if not no_footer:
        print_footer(console)


@click.command()
@click.option(
    "-p",
    "--port",
    default=None,
    type=int,
    help="Restart local server on given port",
)
@click.option("-d", "--develop", is_flag=True, help="Start local server in developer mode")
@click.option(
    "--no-cluster",
    is_flag=True,
    required=False,
    show_default=True,
    default=False,
    help="Restart server without Dask cluster",
)
@click.option(
    "--with-cluster",
    is_flag=True,
    required=False,
    show_default=True,
    default=False,
    help="Restart server with Dask cluster",
)
@click.pass_context
def restart(ctx, port: bool, develop: bool, no_cluster: bool, with_cluster: bool) -> None:
    """
    Restart a local server
    """

    if no_cluster and with_cluster:
        raise ValueError(
            "Options '--no-cluster' and '--with-cluster' are mutually exclusive, please choose one at most."
        )

    if no_cluster:
        set_config("sdk.no_cluster", "true")

    if with_cluster:
        set_config("sdk.no_cluster", "false")

    no_cluster_map = {"true": True, "false": False}
    configuration = {
        "port": port or get_config("dispatcher.port"),
        "develop": develop or (get_config("sdk.log_level") == "debug"),
        "no_cluster": no_cluster_map[get_config("sdk.no_cluster")],
        "mem_per_worker": get_config("dask.mem_per_worker"),
        "threads_per_worker": get_config("dask.threads_per_worker"),
        "workers": get_config("dask.num_workers"),
        "no_header": True,
    }

    ctx.invoke(stop, no_footer=True)
    console = Console()
    console.print()
    ctx.invoke(start, **configuration)


@click.command()
def status() -> None:
    """
    Display local server status
    """

    console = Console()
    print_header(console)

    console.print(Panel("Service Status", expand=False, border_style="blue"))
    console.print()

    with Status("Checking Covalent's Process ID...", console=console):
        pid = _read_pid(UI_PIDFILE)
        port = get_config("dispatcher.port")
        exists = psutil.pid_exists(pid)

    status_table = Table()
    status_table.add_column("Component", style="bold")
    status_table.add_column("Status", style="bold")

    if exists and pid != -1:
        status_table.add_row(
            "Covalent Server", f"[green]Running[/green] at http://localhost:{port}"
        )
    elif exists and psutil.Process(pid).status() == psutil.STATUS_ZOMBIE:
        status_table.add_row(
            "Covalent Server", "[yellow]Zombie process :zombie:[/yellow] - Recommend restart"
        )
    elif not exists or psutil.Process(pid).status() == psutil.STATUS_STOPPED:
        _rm_pid_file(UI_PIDFILE)
        status_table.add_row("Covalent Server", "[red]Stopped[/red]")

    if exists and pid != -1:
        if Path(get_config("dispatcher.heartbeat_file")).is_file():
            with open(get_config("dispatcher.heartbeat_file")) as f:
                last_seen = f.read().split(" ", 1)[1]
            status_table.add_row("", f"Last seen {last_seen}")
        response = requests.get(
            f"http://localhost:{port}/api/v1/dispatches/list?status_filter=RUNNING", timeout=1
        )
        running_workflows = response.json()["total_count"]
        status_table.add_row("", f"There are {running_workflows} workflows currently running.")

    admin_address = _get_cluster_admin_address()
    loop = asyncio.get_event_loop()
    cluster_status = (
        loop.run_until_complete(_get_cluster_status(admin_address)) if admin_address else None
    )

    if _is_server_running() and cluster_status:
        status_table.add_row("Dask Cluster", f"[green]Running[/green] at {admin_address}")
        client = Client(get_config("dask.scheduler_address"))
        running_tasks = len([task for k, v in client.processing().items() for task in v])
        status_table.add_row("", f"There are {running_tasks} tasks currently running.")
    else:
        status_table.add_row("Dask Cluster", "[red]Stopped[/red]")

    try:
        response = requests.get(f"http://localhost:{port}/api/triggers/status", timeout=1)
        trigger_status = response.json()["status"]
    except requests.exceptions.ConnectionError:
        trigger_status = "stopped"

    if trigger_status == "running":
        status_table.add_row("Triggers Server", "[green]Running[/green]")
    else:
        status_table.add_row("Triggers Server", "[red]Stopped[/red]")

    try:
        db = DataStore.factory()

        if db.is_migration_pending:
            status_table.add_row("Database", "[yellow]Migration pending[/yellow]")
        else:
            url = db.db_URL
            if os.environ.get("COVALENT_DATABASE_URL"):
                url = furl(url).origin
            status_table.add_row("Database", f"[green]Connected[/green] at {url}")

    except sqlalchemy.exc.OperationalError:
        status_table.add_row("Database", "[red]Disconnected[/red]")

    console.print(status_table, width=80)

    if cluster_status:
        console.print(
            "\nFor additional information about the Dask cluster, use 'covalent cluster --status'"
        )

    print_footer(console)


@click.command()
@click.option(
    "-H",
    "--hard",
    is_flag=True,
    help="Delete Covalent and workflow data. [default: False]",
)
@click.option(
    "-y", "--yes", is_flag=True, help="Approve without showing the warning. [default: False]"
)
@click.option("--hell-yeah", is_flag=True, hidden=True)
@click.pass_context
def purge(ctx, hard: bool, yes: bool, hell_yeah: bool) -> None:
    """
    Purge Covalent from this system
    """
    cm = ConfigManager()

    console = Console()

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
        warning_text = Text("WARNING", style="bold yellow")
        warning_panel = Panel(warning_text, style="yellow", expand=False, padding=(0, 10))
        console.print(warning_panel)

        console.print("\nPurging will perform the following operations: ")

        console.print("0. Cancel all running workflows")
        console.print("1. Stop all services")

        for i, rem_path in enumerate(removal_list, start=2):
            if os.path.isdir(rem_path):
                console.print(f"{i}. {rem_path} directory will be deleted", style="red")
            else:
                console.print(f"{i}. {rem_path} file will be deleted", style="red")

        if hard:
            console.print("WARNING: All user data will be deleted", style="bold red")

        ans = Prompt.ask(  # Use Prompt.ask instead of console.Prompt.ask
            "\nAre you sure you want to continue?", choices=["y", "n"], default="n"
        )
        if ans == "n":
            console.print("Purge aborted.")
            print_footer(console)
            return

    # Shutdown covalent server
    console.print()
    ctx.invoke(stop, no_header=True, no_footer=True)

    # Remove all directories and files
    for rem_path in removal_list:
        if os.path.isdir(rem_path):
            shutil.rmtree(rem_path, ignore_errors=True)
        else:
            with contextlib.suppress(FileNotFoundError):
                os.remove(rem_path)

        console.print(f"Removed {rem_path}")

    print_footer(console)


@click.command()
def logs() -> None:
    """
    Display local server logs
    """
    console = Console()
    if os.path.exists(UI_LOGFILE):
        with open(UI_LOGFILE, "r") as logfile:
            log_content = logfile.read()
            syntax = Syntax(log_content, "log", theme="monokai", line_numbers=True, word_wrap=True)
            console.print(syntax)
    else:
        console.print(
            f"{UI_LOGFILE} not found. Restart the server to create a new log file.",
            style="bold red",
        )


@click.command()
@click.argument("result_pickle_path")
def migrate_legacy_result_object(result_pickle_path) -> None:
    """Migrate a legacy result object

    Example: `covalent migrate-legacy-result-object result.pkl`
    """

    migrate_pickled_result_object(result_pickle_path)


# Cluster CLI handlers (client side wrappers for the async handlers exposed
# in the dask cluster process)
async def _get_cluster_status(uri: str):
    """
    Returns status of all workers and scheduler in the cluster
    """

    try:
        async with rpc(uri, timeout=2) as r:
            cluster_status = await r.cluster_status()
    except (ConnectionRefusedError, CommClosedError, asyncio.exceptions.TimeoutError, OSError):
        return False
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


def _get_cluster_admin_address():
    try:
        admin_host = get_config("dask.admin_host")
        admin_port = get_config("dask.admin_port")
        admin_server_addr = unparse_address("tcp", f"{admin_host}:{admin_port}")
        return admin_server_addr
    except KeyError:
        return


@click.command()
@click.option("--status", is_flag=True, help="Display Dask cluster status")
@click.option("--info", is_flag=True, help="Display Dask cluster info")
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
    Manage local server's Dask cluster
    """

    loop = asyncio.get_event_loop()
    admin_server_addr = _get_cluster_admin_address()

    console = Console()
    print_header(console)
    console.print(Panel("Covalent Dask Cluster", expand=False, border_style="blue"))
    console.print()

    def print_json(data):
        table = Table()
        table.add_column("Key")
        table.add_column("Value")

        if isinstance(data, dict):
            for key, value in data.items():
                table.add_row(key, str(value))
        elif isinstance(data, tuple):
            for idx, value in enumerate(data):
                table.add_row(str(idx), str(value))
        elif isinstance(data, int):
            table.add_row("Size", str(data))

        console.print(table)

    cluster_status = (
        loop.run_until_complete(_get_cluster_status(admin_server_addr))
        if admin_server_addr
        else None
    )
    if _is_server_running() and cluster_status:
        if status:
            print_json(dict(natsorted(cluster_status.items())))
            degraded = {k: v for k, v in cluster_status.items() if v != "running"}
            if degraded:
                console.print(
                    "\nDask Cluster Status: :face_with_thermometer: Running - Degraded",
                    style="bold",
                )
            else:
                console.print(
                    "\nDask Cluster Status: [green]:heavy_check_mark:[/green] Running - Healthy",
                    style="bold",
                )
            diagnostics_dashboard_addr = get_config("dask.dashboard_link")
            console.print(f"Diagnostics Dashboard: {diagnostics_dashboard_addr} (requires bokeh)")

        elif info:
            print_json(loop.run_until_complete(_get_cluster_info(admin_server_addr)))
        elif address:
            print_json(loop.run_until_complete(_get_cluster_address(admin_server_addr)))
        elif size:
            print_json(loop.run_until_complete(_get_cluster_size(admin_server_addr)))
        elif restart:
            with Status("Restarting the cluster...", spinner="dots") as status:
                loop.run_until_complete(_cluster_restart(admin_server_addr))
                status.update("Cluster restarted")
                console.print("\n")
                console.print(
                    Panel("Cluster restarted", box=ROUNDED, expand=False, border_style="green")
                )
        elif logs:
            console.print(
                "\n".join(
                    [
                        " ".join(x)
                        for x in loop.run_until_complete(_get_cluster_logs(admin_server_addr))[0]
                    ]
                )
            )
        elif scale:
            with Status("Scaling the cluster...", spinner="dots") as status:
                loop.run_until_complete(_cluster_scale(admin_server_addr, nworkers=scale))
                status.update(f"Cluster scaled to {scale} workers")
                console.print(
                    Panel(
                        f"Cluster scaled to {scale} workers",
                        box=ROUNDED,
                        expand=False,
                        border_style="green",
                    )
                )
    else:
        console.print("Dask Cluster Status: [red]:heavy_multiplication_x:[/red] Stopped")

    print_footer(console)


@click.command()
def config() -> None:
    """Display the Covalent configuration"""

    cm = ConfigManager()

    console = Console()
    print_header(console)
    console.print(Panel("Covalent Configuration", expand=False, border_style="blue"))
    console.print()

    cm.read_config()
    config_data = json.loads(json.dumps(cm.config_data, sort_keys=True))
    sorted_sections = ["sdk", "dispatcher", "dask", "executors"]

    for section in sorted_sections:
        keys = config_data[section]

        # Create a table for each section
        section_table = Table(title=f"[bold]{section}[/bold]", title_style="bold")
        section_table.add_column("Key", style="bold")
        section_table.add_column("Value", style="bold")

        for key in keys:
            section_table.add_row(key, str(config_data[section][key]))

        # Wrap the table in a panel
        section_panel = Panel(
            section_table, expand=False, border_style="blue", padding=(0, 1), width=80
        )

        console.print(section_panel)

    print_footer(console)
