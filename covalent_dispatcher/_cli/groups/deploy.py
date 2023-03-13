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

import click

from covalent.cloud_resource_manager.cloud_resource_manager import CloudResourceManager
from covalent.executor import _executor_manager


@click.group(invoke_without_command=True)
@click.argument("executor_name", nargs=1)
@click.pass_context
def deploy(ctx: click.Context, executor_name: str):
    """
    Load the executor plugin installation path based on the executor name provided.
    Will raise KeyError if the `executor_name` plugin is not installed
    """
    executor_module_path = Path(
        __import__(_executor_manager.executor_plugins_map[executor_name].__module__).__path__[0]
    )
    ctx.obj = {"executor_name": executor_name, "executor_module_path": executor_module_path}


@click.command
@click.argument("options", nargs=-1)
@click.pass_obj
def up(executor_metadata: dict, options):
    executor_name = executor_metadata["executor_name"]
    executor_module_path = executor_metadata["executor_module_path"]
    cmd_options = dict(opt.split("=") for opt in options)

    # Create the cloud resource manager and deploy the resources
    crm = CloudResourceManager(executor_name, executor_module_path, cmd_options)
    click.echo(asyncio.run(crm.up()))


@click.command
@click.argument("options", nargs=-1)
@click.pass_obj
def down(executor_metadata: dict, options):
    executor_name = executor_metadata["executor_name"]
    executor_module_path = executor_metadata["executor_module_path"]
    cmd_options = dict(opt.split("=") for opt in options)

    # Create the cloud resource manager and teardown the resources
    crm = CloudResourceManager(executor_name, executor_module_path, cmd_options)
    click.echo(asyncio.run(crm.down()))


@click.command
@click.pass_obj
def status(executor_metadata: dict):
    executor_name = executor_metadata["executor_name"]
    executor_module_path = executor_metadata["executor_module_path"]
    click.echo(executor_module_path)


deploy.add_command(up)
deploy.add_command(down)
deploy.add_command(status)
