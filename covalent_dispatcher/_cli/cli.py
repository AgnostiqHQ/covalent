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
from platform import machine, python_version, system

import click
from rich.console import Console

from .groups import db, deploy
from .service import (
    cluster,
    config,
    logs,
    migrate_legacy_result_object,
    print_header,
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
    The Covalent CLI is used to manage and configure Covalent servers.
    """

    console = Console()

    if version:
        print_header(console)
        console.print("Copyright (C) 2021 Agnostiq Inc.", highlight=False)
        console.print(
            f"Using Python {python_version()} on {system()}-{machine()}", highlight=False
        )
        console.print(f"Release version {metadata.version('covalent')}", highlight=False)
    elif ctx.invoked_subcommand is None:
        # Display the help menu if no command was provided
        ctx = click.get_current_context()
        console.print(ctx.get_help())


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
cli.add_command(deploy)

if __name__ == "__main__":
    cli()
