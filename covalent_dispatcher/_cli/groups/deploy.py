# Copyright 2023 Agnostiq Inc.
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


"""Covalent deploy CLI group."""


import subprocess
from pathlib import Path
from typing import Dict, Tuple

import boto3
import click
from rich.console import Console
from rich.table import Table

from covalent.cloud_resource_manager.core import CloudResourceManager
from covalent.executor import _executor_manager

RESOURCE_ALREADY_EXISTS = "Resources already deployed"
RESOURCE_ALREADY_DESTROYED = "Resources already destroyed"
COMPLETED = "Completed"


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


def get_print_callback(
    console: Console, console_status: Console.status, prepend_msg: str, verbose: bool
):
    """Get print callback method.

    Args:
        console: Rich console object.
        console_status: Console status object.
        prepend_msg: Message to prepend to the output.
        verbose: Whether to print the output inline or not.

    Returns:
        Callback method.

    """
    if verbose:
        return console.print

    def inline_print_callback(msg):
        console_status.update(f"{prepend_msg} {msg}")

    return inline_print_callback


def get_settings_table(crm: CloudResourceManager) -> Table:
    """Get resource provisioning settings table.

    Args:
        crm: CloudResourceManager object.

    Returns:
        Table with resource provisioning settings.

    """
    table = Table(title="Settings")
    table.add_column("Argument", justify="left")
    table.add_column("Value", justify="left")
    for argument in crm.plugin_settings:
        table.add_row(argument, str(crm.plugin_settings[argument]["value"]))
    return table


def get_up_help_table(crm: CloudResourceManager) -> Table:
    """Get resource provisioning help table.

    Args:
        crm: CloudResourceManager object.

    Returns:
        Table with resource provisioning help.

    """
    table = Table()
    table.add_column("Argument", justify="center")
    table.add_column("Required", justify="center")
    table.add_column("Default", justify="center")
    table.add_column("Current value", justify="center")
    for argument in crm.plugin_settings:
        table.add_row(
            argument,
            crm.plugin_settings[argument]["required"],
            str(crm.plugin_settings[argument]["default"]),
            str(crm.plugin_settings[argument]["value"]),
        )
    return table


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
def up(executor_name: str, vars: Dict, help: bool, dry_run: bool, verbose: bool) -> None:
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
    if msg := validate_args(cmd_options):
        click.echo(msg)
        return
    crm = get_crm_object(executor_name, cmd_options)
    if help:
        click.echo(Console().print(get_up_help_table(crm)))
        return

    console = Console(record=True)
    prepend_msg = "[bold green] Provisioning resources..."

    with console.status(prepend_msg) as status:
        try:
            crm.up(
                dry_run=dry_run,
                print_callback=get_print_callback(
                    console=console,
                    console_status=status,
                    prepend_msg=prepend_msg,
                    verbose=verbose,
                ),
            )
        except subprocess.CalledProcessError as e:
            click.echo(f"Unable to provision resources due to the following error:\n\n{e}")
            return

    click.echo(Console().print(get_settings_table(crm)))
    exists_msg_with_verbose = "Apply complete! Resources: 0 added, 0 changed, 0 destroyed"
    exists_msg_without_verbose = "found no differences, so no changes are needed"
    export_data = console.export_text()
    if exists_msg_with_verbose in export_data or exists_msg_without_verbose in export_data:
        click.echo(RESOURCE_ALREADY_EXISTS)
    else:
        click.echo(COMPLETED)


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

    console = Console(record=True)
    prepend_msg = "[bold green] Destroying resources..."
    with console.status(prepend_msg) as status:
        try:
            crm.down(
                print_callback=get_print_callback(
                    console=console,
                    console_status=status,
                    prepend_msg=prepend_msg,
                    verbose=verbose,
                )
            )
        except subprocess.CalledProcessError as e:
            click.echo(f"Unable to destroy resources due to the following error:\n\n{e}")
            return
    destroyed_msg = "Destroy complete! Resources: 0 destroyed."
    export_data = console.export_text()
    if destroyed_msg in export_data:
        click.echo(RESOURCE_ALREADY_DESTROYED)
    else:
        click.echo(COMPLETED)


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
        "up": "Provisioned Resources.",
        "down": "No infrastructure provisioned.",
        "*up": "Warning: Provisioning error, retry 'up'.",
        "*down": "Warning: Teardown error, retry 'down'.",
    }

    if not executor_names:
        executor_names = [
            name
            for name in _executor_manager.executor_plugins_map.keys()
            if name not in ["dask", "local", "remote_executor"]
        ]
        click.echo(f"Executors: {', '.join(executor_names)}")

    table = Table()
    table.add_column("Executor", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Description", justify="center")

    invalid_executor_names = []
    for executor_name in executor_names:
        try:
            crm = get_crm_object(executor_name)
            status = crm.status()
            table.add_row(executor_name, status, description[status])
        except KeyError:
            invalid_executor_names.append(executor_name)

    click.echo(Console().print(table))

    if invalid_executor_names:
        click.echo(
            click.style(
                f"Warning: {', '.join(invalid_executor_names)} are not valid executors.",
                fg="yellow",
            )
        )


def validate_args(args: dict):
    message = None
    if len(args) == 0:
        return message
    if "region" in args and args["region"] != "":
        if not validate_region(args["region"]):
            return f"Unable to find the provided region: {args['region']}"


def validate_region(region_name: str):
    ec2_client = boto3.client("ec2")
    response = ec2_client.describe_regions()
    exists = region_name in [item["RegionName"] for item in response["Regions"]]
    return exists
