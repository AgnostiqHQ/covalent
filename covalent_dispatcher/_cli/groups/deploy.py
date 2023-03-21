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


import sys
from pathlib import Path

import click

from covalent.cloud_resource_manager.cloud_resource_manager import CloudResourceManager
from covalent.executor import _executor_manager

CURRENT_MODULE = sys.modules[__name__]

INSTALLED_CLOUD_EXECUTORS = [
    key
    for key, _ in _executor_manager.executor_plugins_map.items()
    if key not in ["dask", "local", "remote_executor"]
]

CLOUD_EXECUTOR_MODULES = {
    f"{name}": __import__(_executor_manager.executor_plugins_map[name].__module__)
    for name in INSTALLED_CLOUD_EXECUTORS
}

CLOUD_EXECUTOR_OPTIONS = {
    f"{name}": [
        (
            key,
            str(value.required),
        )
        for key, value in CLOUD_EXECUTOR_MODULES[name].ExecutorInfraDefaults.__fields__.items()
    ]
    for name in INSTALLED_CLOUD_EXECUTORS
}


@click.group()
@click.argument(
    "executor", nargs=1, type=click.Choice(INSTALLED_CLOUD_EXECUTORS, case_sensitive=True)
)
@click.pass_context
def deploy(ctx: click.Context, executor: str):
    for key, value in CLOUD_EXECUTOR_OPTIONS[executor]:
        click.option("--" + key, required=False)(CURRENT_MODULE.deploy.commands["up"])
    ctx.obj = {"executor_name": executor}


@deploy.command
@click.option("--dry-run", is_flag=True)
@click.pass_context
def up(ctx, dry_run, *args, **kwargs):
    """
    Load the executor plugin installation path based on the executor name provided.
    """
    executor_name = ctx.obj["executor_name"]
    executor_module = CLOUD_EXECUTOR_MODULES[executor_name]
    executor_module_path = Path(executor_module.__path__[0])

    click.echo(kwargs)
    crm = CloudResourceManager(executor_name, str(executor_module_path), kwargs)
    click.echo(crm.up(dry_run))


@deploy.command
@click.option("--dry-run", is_flag=True, help="Do a dry run")
@click.pass_context
def down(ctx, dry_run: bool, *args, **kwargs):
    executor_name = ctx.obj["executor_name"]
    executor_module = CLOUD_EXECUTOR_MODULES[executor_name]
    executor_module_path = Path(executor_module.__path__[0])

    # Create the cloud resource manager and teardown the resources
    crm = CloudResourceManager(executor_name, str(executor_module_path), kwargs)
    click.echo(crm.down(dry_run))


@deploy.command
@click.pass_obj
def status(executor_metadata: dict):
    executor_module_path = executor_metadata["executor_module_path"]
    click.echo(executor_module_path)
