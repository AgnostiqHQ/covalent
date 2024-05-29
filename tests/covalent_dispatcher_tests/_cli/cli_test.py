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
    from covalent_dispatcher._cli.groups.deploy_group import _run_command_and_show_output

    mock_console_print = mocker.patch("rich.console.Console.print")
    mock_click_echo = mocker.patch("click.echo")
    mocker.patch(
        "covalent_dispatcher._cli.groups.deploy_group_print_callbacks.ScrollBufferCallback.complete_msg",
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


@pytest.mark.parametrize(
    ("verbose", "mode"),
    [
        (False, "provision"),
        (False, "destroy"),
        (True, "provision"),
        (True, "destroy"),
    ],
)
def test_scroll_buffer_print_callback(mocker, verbose, mode):
    """
    Unit test for the custom buffered print callback.
    """
    from rich.console import Console
    from rich.status import Status

    from covalent_dispatcher._cli.groups.deploy_group import _TEMPLATE
    from covalent_dispatcher._cli.groups.deploy_group_print_callbacks import ScrollBufferCallback

    console = Console(record=True)
    console_status = Status("Testing...", console=console)

    mock_print = mocker.patch("covalent_dispatcher._cli.groups.deploy_group_print_callbacks.print")
    mock_console_status_update = mocker.patch("rich.status.Status.update")

    print_callback = ScrollBufferCallback(
        console=console,
        console_status=console_status,
        msg_template=_TEMPLATE.format(message="Testing...", text="{text}"),
        verbose=verbose,
        max_lines=3,  # shorten to hit pop inside `._inline_print`
    )

    complete_msg = (
        "Apply complete! Resources: 19 added, 0 changed, 0 destroyed."
        if mode == "provision"
        else "Destroy complete! Resources: 19 destroyed."
    )
    messages = ["fake", "fake", "fake", complete_msg, "fake", "fake", "fake"]

    for msg in messages:
        print_callback(msg)
        if verbose:
            mock_print.assert_called_with(msg)
        else:
            mock_console_status_update.assert_called_with(
                print_callback.msg_template.format(text=print_callback.render_buffer())
            )

    if not verbose:
        assert print_callback.complete_msg == complete_msg


def test_deploy_up(mocker):
    """
    Unit test for `covalent deploy up [executor_name]` command.
    """

    from covalent_dispatcher._cli.groups.deploy_group import up

    # Patch function that executes commands.
    mock_run_command_and_show_output = mocker.patch(
        "covalent_dispatcher._cli.groups.deploy_group._run_command_and_show_output",
    )

    # Fail with invalid executor name
    with pytest.raises(SystemExit) as exc_info:
        ctx = click.Context(up)
        ctx.invoke(up, executor_name="invalid")

    assert exc_info.value.code == 1

    # Succeed but exit after help message.
    mocker.patch(
        "covalent_dispatcher._cli.groups.deploy_group.get_crm_object",
    )
    with pytest.raises(SystemExit) as exc_info:
        ctx = click.Context(up)
        ctx.invoke(up, help=True)

    assert exc_info.value.code == 0

    # Succeed with valid command options.
    ctx = click.Context(up)
    ctx.invoke(up, verbose=True)

    mock_run_command_and_show_output.assert_called_once()


def test_deploy_down(mocker):
    """
    Unit test for `covalent deploy down [executor_name]` command.
    """

    from covalent_dispatcher._cli.groups.deploy_group import down

    # Patch function that executes commands.
    mock_run_command_and_show_output = mocker.patch(
        "covalent_dispatcher._cli.groups.deploy_group._run_command_and_show_output",
    )

    # Fail with invalid executor name
    with pytest.raises(SystemExit) as exc_info:
        ctx = click.Context(down)
        ctx.invoke(down, executor_name="invalid")

    assert exc_info.value.code == 1

    # Succeed with valid command options.
    mocker.patch(
        "covalent_dispatcher._cli.groups.deploy_group.get_crm_object",
    )

    ctx = click.Context(down)
    ctx.invoke(down, verbose=True)
    mock_run_command_and_show_output.assert_called_once()


def test_deploy_status(mocker):
    """
    Unit test for `covalent deploy status [executor_name]` command.
    """

    from covalent.executor import _executor_manager
    from covalent_dispatcher._cli.groups.deploy_group import status

    # Succeed with empty `executor_names` argument.
    # Ignoring extra plugin(s) discovered in CI tests environment.
    filtered_plugins_map = {
        k: v
        for k, v in _executor_manager.executor_plugins_map.items()
        if k not in ["timing_plugin"]
    }
    mock_executor_manager = mocker.patch.object(
        _executor_manager,
        "executor_plugins_map",
        return_value=filtered_plugins_map,
    )

    ctx = click.Context(status)
    ctx.invoke(status, executor_names=[])
    mocker.stop(mock_executor_manager)  # stop ignoring any plugins

    # Succeed with invalid `executor_names` argument.
    mock_click_style = mocker.patch("click.style")

    ctx = click.Context(status)
    ctx.invoke(status, executor_names=["invalid"])

    mock_click_style.assert_called_once()

    # Succeed with 'valid' `executor_names` argument.
    mocker.patch(
        "covalent_dispatcher._cli.groups.deploy_group.get_crm_object",
    )
    mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager.status",
        return_value="down",
    )

    mock_console_print = mocker.patch("rich.console.Console.print")

    ctx = click.Context(status)
    ctx.invoke(status, executor_names=["awsbatch"])  # OK if not installed

    mock_console_print.assert_called_once()
