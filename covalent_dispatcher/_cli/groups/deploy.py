# Copyright 2023 Agnostiq Inc.
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


import asyncio
from pathlib import Path
from typing import Dict, Tuple

import click
from rich.console import Console
from rich.table import Table

from covalent.cloud_resource_manager.cloud_resource_manager import CloudResourceManager
from covalent.executor import _executor_manager


# TODO - Check if this should go in the executor manager.
def get_executor_module_path(executor_name: str) -> Path:
    """
    Get the executor module path based on the executor name provided.
    Will raise KeyError if the `executor_name` plugin is not installed

    Args:
        executor_name: Name of executor to get module path for.

    Returns:
        Path to executor module.

    """
    return Path(
        __import__(_executor_manager.executor_plugins_map[executor_name].__module__).__path__[0]
    )


@click.group(invoke_without_command=True)
def deploy():
    """
    Covalent deploy group with options to:

    1. Spin resources up via `covalent deploy up <executor_name> <options>`.
    2. Tear resources down via `covalent deploy down <executor_name> <options>`.
    3. Show status of resources via `covalent deploy status <executor_name>`.
    4. Show status of all resources via `covalent deploy status`.

    """
    pass


@deploy.command()
@click.argument("executor_name", nargs=1)
@click.argument("options", nargs=-1)
def up(executor_name: str, options: Dict) -> None:
    """Spin up resources corresponding to executor.

    Args:
        executor_name: Short name of executor to spin up.
        options: Options to pass to the Cloud Resource Manager when provisioning the resources.

    Returns:
        None

    Examples:
        $ covalent deploy up awsbatch region=us-east-1 instance-type=t2.micro
        $ covalent deploy up ecs

    """
    cmd_options = dict(opt.split("=") for opt in options)
    executor_module_path = get_executor_module_path(executor_name)
    crm = CloudResourceManager(executor_name, executor_module_path, cmd_options)
    click.echo(asyncio.run(crm.up()))


@deploy.command()
@click.argument("executor_name", nargs=1)
def down(executor_name: str) -> None:
    """Teardown resources corresponding to executor.

    Args:
        executor_name: Short name of executor to spin up.

    Returns:
        None

    Examples:
        $ covalent deploy down awsbatch
        $ covalent deploy down ecs

    """
    executor_module_path = get_executor_module_path(executor_name)
    crm = CloudResourceManager(executor_name, executor_module_path)
    click.echo(asyncio.run(crm.down()))


@deploy.command()
@click.argument("executor_names", nargs=-1, required=False)
def status(executor_names: Tuple[str]) -> None:
    """Show executor resource provision status.

    Args:
        executor_names: Short name(s) of executor to show status for.

    Returns:
        None

    Examples:
        $ covalent deploy status awsbatch
        $ covalent deploy status awsbatch ecs
        $ covalent deploy status

    """
    if not executor_names:
        executor_names = _executor_manager.executor_plugins_map.keys()

    table = Table()
    table.add_column("Executor", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Description", justify="center")

    for executor_name in executor_names:
        executor_module_path = get_executor_module_path(executor_name)
        crm = CloudResourceManager(executor_name, executor_module_path)
        status, description = asyncio.run(crm.status())

        table.add_row(executor_name, status, description)

    console = Console()
    click.echo(console.print(table))
