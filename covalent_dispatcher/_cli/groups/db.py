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
from os import path
from pathlib import Path
from subprocess import PIPE, Popen

import click

from covalent._data_store.datastore import DataStore

MIGRATION_WARNING_MSG = "There was an issue running migrations.\nPlease read https://covalent.readthedocs.io/en/latest/how_to/db/migration_error.html for more information."


@click.group(invoke_without_command=True)
@click.pass_context
def db(ctx: click.Context):
    """
    Group of utility commands to manage dispatcher database
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@click.command()
@click.pass_context
def migrate(ctx: click.Context) -> None:
    """
    Run DB Migrations programatically
    """
    try:
        db = DataStore.factory()
        db.run_migrations()
        click.secho("Migrations are up to date.", fg="green")
    except Exception as migration_error:
        click.echo(str(migration_error))
        click.secho(MIGRATION_WARNING_MSG, fg="red")
        return ctx.exit(1)


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.pass_context
@click.argument("alembic_args", nargs=-1, type=click.UNPROCESSED)
def alembic(ctx: click.Context, alembic_args) -> None:
    """
    Expose alembic CLI to be used via covalent CLI
    """
    try:
        alembic_args = list(alembic_args)
        migrations_folder_path = Path(path.join(__file__, "./../../../../covalent_migrations/"))
        project_root_path = migrations_folder_path / Path("..")
        settings_file_path = migrations_folder_path / Path("alembic.ini")
        alembic_command = ["alembic", "-c", str(settings_file_path.resolve())] + alembic_args
        p = Popen(alembic_command, stdout=PIPE, stderr=PIPE, cwd=str(project_root_path.resolve()))
        output, error = p.communicate()
        if error:
            click.echo(error.decode("utf-8").strip())
        else:
            click.echo(output.decode("utf-8").strip())
    except Exception as migration_error:
        if migration_error:
            click.echo(f"{type(migration_error)}:{str(migration_error)}")
        click.secho(
            "There was an error forwarding arguments to alembic CLI please ensure that alembic is installed.",
            fg="red",
        )
        return ctx.exit(1)


db.add_command(alembic)
db.add_command(migrate)
