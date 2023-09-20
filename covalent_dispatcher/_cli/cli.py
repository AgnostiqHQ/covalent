#!/usr/bin/env python

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

"""Covalent CLI Tool."""

from importlib import metadata

import click

from .groups import db
from .service import (
    cluster,
    config,
    logs,
    migrate_legacy_result_object,
    purge,
    restart,
    start,
    status,
    stop,
)


# Main entrypoint
@click.group(invoke_without_command=True)
@click.option("-v", "--version", is_flag=True, help="Display version information.")
@click.pass_context
def cli(ctx: click.Context, version: bool) -> None:
    """
    Covalent CLI tool used to manage the servers.
    """
    if version:
        click.echo("covalent:  Covalent Workflow CLI Tool")
        click.echo("Copyright (C) 2021 Agnostiq Inc.")
        click.echo("Built using Python 3.8 (Platform: x86_64-linux)")
        click.echo(f"Release version {metadata.version('covalent')}")
    elif ctx.invoked_subcommand is None:
        # Display the help menu if no command was provided
        ctx = click.get_current_context()
        click.echo(ctx.get_help())


# Server management
cli.add_command(start)
cli.add_command(stop)
cli.add_command(restart)
cli.add_command(status)
cli.add_command(purge)
cli.add_command(logs)
cli.add_command(cluster)
cli.add_command(db)
cli.add_command(config)
cli.add_command(migrate_legacy_result_object)

if __name__ == "__main__":
    cli()
