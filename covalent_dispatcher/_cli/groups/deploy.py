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


from pathlib import Path

import click
from click import Context, HelpFormatter
from pydantic.error_wrappers import ValidationError

from covalent.cloud_resource_manager.cloud_resource_manager import CloudResourceManager
from covalent.executor import _executor_manager


class CustomCommand(click.Command):
    def _get_cmd_options(self, executor_module):
        """
        Return a sequence of cmd args based on the executor module
        """
        cmd_opts = [
            (
                key,
                str(value.required),
            )
            for key, value in executor_module.ExecutorInfraDefaults.__fields__.items()
        ]
        cmd_opts.insert(
            0,
            (
                "NAME",
                "REQUIRED",
            ),
        )
        return cmd_opts

    def format_help_text(self, ctx: Context, formatter: HelpFormatter) -> None:
        executor_module = ctx.obj["executor_module"]
        cmd_options = self._get_cmd_options(executor_module)
        formatter.write_heading("Command options")
        formatter.write_dl(cmd_options)


@click.group()
@click.argument(
    "executor_name",
    nargs=1,
    required=True,
    type=click.Choice(["awsbatch", "gcpbatch", "awslambda"], case_sensitive=True),
)
@click.pass_context
def deploy(ctx: click.Context, executor_name: str):
    """
    Load the executor plugin installation path based on the executor name provided.
    """
    executor_module = __import__(_executor_manager.executor_plugins_map[executor_name].__module__)
    executor_module_path = Path(executor_module.__path__[0])

    ctx.obj = {
        "executor_name": executor_name,
        "executor_module": executor_module,
        "executor_module_path": executor_module_path,
    }


@deploy.command(cls=CustomCommand)
@click.argument(
    "action",
    nargs=1,
    required=True,
    type=click.Choice(["up", "down", "status"], case_sensitive=True),
)
def awsbatch():
    pass


@deploy.command(cls=CustomCommand)
@click.argument("options", nargs=-1)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Do a dry run but do not deploy the infrastructure",
)
@click.pass_obj
def up(executor_metadata: dict, options, dry_run: bool):
    executor_name = executor_metadata["executor_name"]
    executor_module = executor_metadata["executor_module"]
    executor_module_path = executor_metadata["executor_module_path"]

    if not hasattr(executor_module, "ExecutorInfraDefaults"):
        raise ValueError(f"ExecutorInfraDefaults not provided for {executor_name} module")

    cmd_options = dict(opt.split("=") for opt in options)

    try:
        executor_infra_defaults = executor_module.ExecutorInfraDefaults(**cmd_options)
        for key, value in dict(executor_infra_defaults).items():
            cmd_options[key] = str(value)
    except ValidationError as err:
        click.echo(str(err))
        return

    # Create the cloud resource manager and deploy the resources
    crm = CloudResourceManager(executor_name, executor_module_path, cmd_options)
    click.echo(crm.up(dry_run))


@deploy.command(cls=CustomCommand)
@click.argument("options", nargs=-1)
@click.option("--dry-run", is_flag=True, help="Do a dry run")
@click.pass_obj
def down(executor_metadata: dict, options, dry_run: bool):
    executor_name = executor_metadata["executor_name"]
    executor_module_path = executor_metadata["executor_module_path"]

    cmd_options = dict(opt.split("=") for opt in options)

    # Create the cloud resource manager and teardown the resources
    crm = CloudResourceManager(executor_name, executor_module_path, cmd_options)
    click.echo(crm.down(dry_run))


@deploy.command(cls=CustomCommand)
@click.pass_obj
def status(executor_metadata: dict):
    executor_module_path = executor_metadata["executor_module_path"]
    click.echo(executor_module_path)
