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
import sys
from functools import partial
from importlib import import_module
from pathlib import Path
from typing import Callable, Dict, Tuple

import boto3
import click
from rich.console import Console
from rich.table import Table

from covalent.cloud_resource_manager.core import CloudResourceManager
from covalent.executor import _executor_manager

from .deploy_group_print_callbacks import ScrollBufferCallback

_TEMPLATE = "[bold green]{message} [default]\n {text}"


def get_crm_object(executor_name: str, options: Dict = None) -> CloudResourceManager:
    """
    Get the CloudResourceManager object.

    Returns:
        CloudResourceManager object.

    """
    executor_plugin = _executor_manager.executor_plugins_map[executor_name]
    executor_module_path = Path(import_module(executor_plugin.__module__).__file__).parent
    return CloudResourceManager(executor_name, executor_module_path, options)


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


def _run_command_and_show_output(
    _command: Callable[[Callable], None], _status_message: str, *, verbose: bool
) -> None:
    """Run the command and show the output in the console.

    This function handles execution and outputs from the `up` and `down` commands.

    Args:
        _command: command to run, e.g. `partial(crm.up, dry_run=dry_run)`
        _status_message: message to show in the console status bar, e.g. "Provisioning resources..."
        verbose: whether to show the full Terraform output or not.
    """
    console = Console(record=True)
    msg_template = _TEMPLATE.format(message=_status_message, text="{text}")

    with console.status(msg_template.format(text="")) as console_status:
        print_callback = ScrollBufferCallback(
            console=console,
            console_status=console_status,
            msg_template=msg_template,
            verbose=verbose,
        )

        try:
            _command(print_callback=print_callback)

        except subprocess.CalledProcessError as e:
            console_status.stop()
            click.echo(e.stdout)  # display error
            sys.exit(1)

        if not verbose:
            console_status.stop()
            if (complete_msg := print_callback.complete_msg) is not None:
                console.print("\n", complete_msg, style="bold green")


@click.group(invoke_without_command=True)
def deploy():
    """
    Covalent deploy group with options to:

    1. Spin resources up via `covalent deploy up <executor_name> <options>`.

    2. Tear resources down via `covalent deploy down <executor_name> <options>`.

    3. Show status of resources via `covalent deploy status <executor_name>`.

    4. Show status of all resources via `covalent deploy status`.

    """


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
        # Message is not None, so there was an error.
        click.echo(msg)
        sys.exit(1)
    crm = get_crm_object(executor_name, cmd_options)
    if help:
        click.echo(Console().print(get_up_help_table(crm)))
        sys.exit(0)

    _command = partial(crm.up, dry_run=dry_run)
    _run_command_and_show_output(_command, "Provisioning resources...", verbose=verbose)


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
    _command = partial(crm.down)
    _run_command_and_show_output(_command, "Destroying resources...", verbose=verbose)


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
            for name in _executor_manager.executor_plugins_map
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
            crm_status = crm.status()
            table.add_row(executor_name, crm_status, description[crm_status])
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
