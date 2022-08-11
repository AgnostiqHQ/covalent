#!/usr/bin/env python

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

"""Covalent CLI Tool."""

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
        from importlib import metadata

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
