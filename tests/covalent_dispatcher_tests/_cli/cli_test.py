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

"""Test for Covalent CLI Tool."""

import subprocess

import click
import pytest
from click.testing import CliRunner

from covalent_dispatcher._cli.cli import cli
from covalent_dispatcher._cli.groups.deploy import _run_command_and_show_output


def test_cli(mocker):
    """Test the main CLI function."""

    importlib_mock = mocker.patch("covalent_dispatcher._cli.cli.metadata")

    with open("VERSION", "r") as f:
        current_version = f.readline()

    importlib_mock.version.return_value = current_version

    runner = CliRunner()
    response = runner.invoke(cli, "--version")

    assert (
        ("python" in response.output.lower())
        and ("agnostiq" in response.output.lower())
        and ("copyright" in response.output.lower())
        and (current_version in response.output.lower())
    )

    response = runner.invoke(cli)
    assert ("options" in response.output.lower()) and ("commands" in response.output.lower())


def test_cli_commands():
    """Test the list of commands associated with Covalent CLI."""

    ctx = click.Context
    assert cli.list_commands(ctx) == [
        "cluster",
        "config",
        "db",
        "deploy",
        "logs",
        "migrate-legacy-result-object",
        "purge",
        "restart",
        "start",
        "status",
        "stop",
    ]


@pytest.mark.parametrize(
    ("error", "verbose"),
    [
        (False, False),
        (False, True),
        (True, False),
        (True, True),
    ],
)
def test_run_command_and_show_output(mocker, error, verbose):
    """
    Unit test for `_run_command_and_show_output` function.

    Test that errors are raised and messages printed when expected.
    """

    mock_console_print = mocker.patch("rich.console.Console.print")
    mock_click_echo = mocker.patch("click.echo")
    mocker.patch(
        "covalent_dispatcher._cli.groups.deploy_print_callbacks.ScrollBufferCallback.complete_msg",
        return_value="Apply complete! Resources: 19 added, 0 changed, 0 destroyed.",
    )

    def _command(*args, **kwargs):
        _command.calls += 1
        _output = "Testing Error..."
        _error = subprocess.CalledProcessError(1, "terraform", _output)
        if error:
            raise _error

    _command.calls = 0

    if error:
        msg = "Testing Error..."
        with pytest.raises(SystemExit):
            _run_command_and_show_output(_command, msg, verbose=verbose)
    else:
        msg = "Testing Success..."
        _run_command_and_show_output(_command, msg, verbose=verbose)

    if error:
        mock_click_echo.assert_called_once_with("Testing Error...")
    elif not verbose:
        mock_console_print.assert_called_once()
    else:
        assert _command.calls == 1
