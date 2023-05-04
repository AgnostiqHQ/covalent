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

from covalent.cloud_resource_manager.core import CloudResourceManager
from covalent.executor import _executor_manager


def get_crm_object(executor_name: str, options: Dict = None) -> CloudResourceManager:
    """
    Get the CloudResourceManager object.

    Returns:
        CloudResourceManager object.

    """
    executor_module_path = Path(
        __import__(_executor_manager.executor_plugins_map[executor_name].__module__).__path__[0]
    )
    return CloudResourceManager(executor_name, executor_module_path, options)


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


@deploy.command(context_settings={"ignore_unknown_options": True})
@click.argument("executor_name", nargs=1)
@click.argument("vars", nargs=-1)
@click.option(
    "--help", "-h", is_flag=True, help="Get info on default and current values for resources."
)
@click.option("--dry-run", "-dr", is_flag=True, help="Get info on current parameter settings.")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show the full Terraform output when provisioning resources.",
)
def up(executor_name: str, vars: Dict, help: bool, dry_run: bool) -> None:
    """Spin up resources corresponding to executor.

    Args:
        executor_name: Short name of executor to spin up.
        options: Options to pass to the Cloud Resource Manager when provisioning the resources.

    Returns:
        None

    Examples:
        $ covalent deploy up awsbatch --region=us-east-1 --instance-type=t2.micro
        $ covalent deploy up ecs
        $ covalent deploy up ecs --help
        $ covalent deploy up awslambda --verbose --region=us-east-1 --instance-type=t2.micro

    """
    cmd_options = {key[2:]: value for key, value in (var.split("=") for var in vars)}
    crm = get_crm_object(executor_name, cmd_options)
    if help:
        table = Table()
        table.add_column("Argument", justify="center")
        table.add_column("Required", justify="center")
        table.add_column("Default", justify="center")
        table.add_column("Current value", justify="center")
        for argument in crm.resource_parameters:
            table.add_row(
                argument,
                crm.resource_parameters[argument]["required"],
                crm.resource_parameters[argument]["default"],
                crm.resource_parameters[argument]["value"],
            )
        click.echo(Console().print(table))
        return

    if dry_run:
        asyncio.run(crm.up(dry_run=dry_run))
        table = Table()
        table.add_column("Settings", justify="center")
        for argument in crm.resource_parameters:
            table.add_row(f"{argument: crm.resource_parameters[argument]['value']}")
        click.echo(Console().print(table))
    else:
        click.echo(asyncio.run(crm.up()))


@deploy.command()
@click.argument("executor_name", nargs=1)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show the full Terraform output when spinning down resources.",
)
def down(executor_name: str, verbose: bool) -> None:
    """Teardown resources corresponding to executor.

    Args:
        executor_name: Short name of executor to spin up.

    Returns:
        None

    Examples:
        $ covalent deploy down awsbatch
        $ covalent deploy down ecs --verbose

    """
    crm = get_crm_object(executor_name)
    click.echo(asyncio.run(crm.down()))


# TODO - Color code status.
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
    description = {
        "up": "Resources are provisioned.",
        "down": "Resources are not provisioned.",
        "*up": "Resources are partially provisioned.",
        "*down": "Resources are partially deprovisioned.",
    }

    if not executor_names:
        executor_names = _executor_manager.executor_plugins_map.keys()

    table = Table()
    table.add_column("Executor", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Description", justify="center")

    invalid_executor_names = []
    for executor_name in executor_names:
        try:
            crm = get_crm_object(executor_name)
            status = asyncio.run(crm.status())
            table.add_row(executor_name, status, description[status])
        except KeyError:
            invalid_executor_names.append(executor_name)

    click.echo(Console().print(table))

    if invalid_executor_names:
        click.echo(
            click.style(
                f"{', '.join(invalid_executor_names)} are not valid executors.", fg="yellow"
            )
        )
