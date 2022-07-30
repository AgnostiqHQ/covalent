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

"""Test for Covalent CLI Tool."""

import click
from click.testing import CliRunner

from covalent_dispatcher._cli.cli import cli


def test_cli(mocker):
    """Test the main CLI function."""

    runner = CliRunner()
    response = runner.invoke(cli, "--version")

    with open("VERSION", "r") as f:
        current_version = f.readline()

    assert (
        ("python" in response.output.lower())
        and ("agnostiq" in response.output.lower())
        and ("copyright" in response.output.lower())
    )

    response = runner.invoke(cli)
    assert ("options" in response.output.lower()) and ("commands" in response.output.lower())


def test_cli_commands():
    """Test the list of commands associated with Covalent CLI."""

    ctx = click.Context
    assert cli.list_commands(ctx) == [
        "cluster",
        "db",
        "logs",
        "purge",
        "restart",
        "start",
        "status",
        "stop",
    ]
