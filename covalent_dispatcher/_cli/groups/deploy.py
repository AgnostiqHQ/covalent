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

import click


@click.group(invoke_without_command=True)
@click.pass_context
def deploy(ctx: click.Context):
    """
    Group of utility commands to deploy executor resources.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.pass_context
def status(ctx: click.Context) -> None:
    """
    Check executor resource status.
    """
    pass


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.pass_context
def up(ctx: click.Context) -> None:
    """
    Check executor resource status.
    """
    pass


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.pass_context
def down(ctx: click.Context) -> None:
    """
    Check executor resource status.
    """
    pass


deploy.add_command(up)
deploy.add_command(down)
deploy.add_command(status)
