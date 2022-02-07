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

"""Tests for Covalent command line interface (CLI) Tool."""

import os
import tempfile
from asyncore import dispatcher
from http import server

import mock
import psutil
import pytest
from click.testing import CliRunner
from psutil import pid_exists

from covalent_dispatcher._cli.service import (
    _graceful_restart,
    _graceful_shutdown,
    _graceful_start,
    _is_dispatcher_running,
    _is_ui_running,
    _next_available_port,
    _port_from_pid,
    _read_pid,
    _rm_pid_file,
    purge,
    restart,
    start,
    status,
    stop,
)


def test_read_pid_nonexistent_file():
    """Test the process id read function when the pid file does not exist."""

    with tempfile.TemporaryDirectory() as tmp_dir:
        assert _read_pid(f"{tmp_dir}/nonexistent.pid") == -1


def test_read_valid_pid_file():
    """Test the process id read function when the pid file exists."""

    with mock.patch("covalent_dispatcher._cli.service.open", mock.mock_open(read_data="1984")):
        res = _read_pid(filename="mock.pid")
    assert res == 1984


@pytest.mark.parametrize("file_exists,remove_call_status", [(False, False), (True, True)])
def test_rm_pid_file(mocker, file_exists, remove_call_status):
    """Test the process id file removal function."""

    mocker.patch("os.path.isfile", return_value=file_exists)
    os_remove_mock = mocker.patch("os.remove")
    _rm_pid_file("nonexistent.pid")

    assert os_remove_mock.called is remove_call_status


def test_port_from_invalid_pid(mocker):
    """Test port retrieval method from invalid pid."""

    mocker.patch("psutil.pid_exists", return_value=False)
    res = _port_from_pid(-1)
    assert res is None


def test_port_from_valid_pid(mocker):
    """Test port retrieval method from invalid pid."""

    process_mock = mocker.patch("psutil.Process")
    mocker.patch("psutil.pid_exists", return_value=True)
    _port_from_pid(12)
    process_mock.assert_called_once()


def test_next_available_port(mocker):
    """Test function to generate the next available port that is not in use."""

    # Case 1 - Port is available.
    mocker.patch("socket.socket.bind")
    res = _next_available_port(requested_port=12)
    assert res == 12

    # Case 2 - Next two ports are not available.
    click_echo_mock = mocker.patch("click.echo")
    mocker.patch(
        "socket.socket.bind", side_effect=[Exception("OSERROR"), Exception("OSERROR"), None]
    )

    res = _next_available_port(requested_port=12)
    assert res == 14
    click_echo_mock.assert_called_once()


def test_graceful_start_when_pid_exists(mocker):
    """Test the graceful server start function."""

    read_pid_mock = mocker.patch("covalent_dispatcher._cli.service._read_pid")
    pid_exists_mock = mocker.patch("psutil.pid_exists", return_value=True)
    port_from_pid_mock = mocker.patch(
        "covalent_dispatcher._cli.service._port_from_pid", return_value=1984
    )
    click_echo_mock = mocker.patch("click.echo")
    res = _graceful_start("", "", "", "", 15, False)
    assert res == 1984

    click_echo_mock.assert_called_once()
    read_pid_mock.assert_called_once()
    pid_exists_mock.assert_called_once()
    port_from_pid_mock.assert_called_once()


def test_graceful_start_when_pid_absent(mocker):
    """Test the graceful server start function."""

    read_pid_mock = mocker.patch("covalent_dispatcher._cli.service._read_pid")
    pid_exists_mock = mocker.patch("psutil.pid_exists", return_value=False)
    rm_pid_file_mock = mocker.patch("covalent_dispatcher._cli.service._rm_pid_file")
    next_available_port_mock = mocker.patch(
        "covalent_dispatcher._cli.service._next_available_port", return_value=1984
    )
    popen_mock = mocker.patch("covalent_dispatcher._cli.service.Popen")
    click_echo_mock = mocker.patch("click.echo")

    res = _graceful_start("", "", "", "", 15, False)
    assert res == 1984

    rm_pid_file_mock.assert_called_once()
    next_available_port_mock.assert_called_once()
    pid_exists_mock.assert_called_once()
    popen_mock.assert_called_once()
    click_echo_mock.assert_called_once()
    read_pid_mock.assert_called_once()


def test_graceful_shutdown_running_server(mocker):
    """Test the graceful shutdown functionality."""

    read_pid_mock = mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=12)
    mocker.patch("psutil.pid_exists", return_value=True)
    process_mock = mocker.patch("psutil.Process")
    rm_pid_file_mock = mocker.patch("covalent_dispatcher._cli.service._rm_pid_file")
    click_echo_mock = mocker.patch("click.echo")

    _graceful_shutdown(server_name="mock", pidfile="mock")

    click_echo_mock.assert_called_once_with("Covalent mock server has stopped.")
    rm_pid_file_mock.assert_called_once_with("mock")
    read_pid_mock.assert_called_once()
    process_mock.assert_called_once_with(12)


def test_graceful_shutdown_stopped_server(mocker):
    """Test the graceful shutdown functionality."""

    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=12)
    mocker.patch("psutil.pid_exists", return_value=False)
    process_mock = mocker.patch("psutil.Process")
    rm_pid_file_mock = mocker.patch("covalent_dispatcher._cli.service._rm_pid_file")
    click_echo_mock = mocker.patch("click.echo")

    _graceful_shutdown(server_name="mock", pidfile="mock")

    click_echo_mock.assert_called_once_with("Covalent mock server was not running.")
    rm_pid_file_mock.assert_called_once_with("mock")
    assert not process_mock.called


def test_graceful_restart_valid_pid(mocker):
    """Test the graceful restart method for a valid pid file and pid."""

    read_pid_mock = mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=20)
    os_kill_mock = mocker.patch("os.kill")
    click_echo_mock = mocker.patch("click.echo")
    mocker.patch("covalent_dispatcher._cli.service._port_from_pid", return_value=15)
    res = _graceful_restart(server_name="mock", pidfile="mock")
    assert res

    os_kill_mock.assert_called_once()
    read_pid_mock.assert_called_once_with("mock")
    click_echo_mock.assert_called_once_with(
        "Covalent mock server has restarted on port http://0.0.0.0:15."
    )


def test_graceful_restart_nonexistent_pid(mocker):
    """Test the graceful restart method for a non-existent pid file."""

    read_pid_mock = mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=-1)
    os_kill_mock = mocker.patch("os.kill")
    click_echo_mock = mocker.patch("click.echo")
    mocker.patch("covalent_dispatcher._cli.service._port_from_pid", return_value=15)
    res = _graceful_restart(server_name="mock", pidfile="mock")
    assert not res
    assert not os_kill_mock.called
    assert not click_echo_mock.called
    read_pid_mock.assert_called_once()


def test_start(mocker, monkeypatch):
    """Test the start CLI command."""

    runner = CliRunner()
    port_val = 42
    graceful_start_mock = mocker.patch(
        "covalent_dispatcher._cli.service._graceful_start", return_value=port_val
    )
    set_config_mock = mocker.patch("covalent_dispatcher._cli.service.set_config")
    monkeypatch.setattr("covalent_dispatcher._cli.service.DISPATCHER_SRVDIR", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.DISPATCHER_PIDFILE", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.DISPATCHER_LOGFILE", "mock")

    runner.invoke(start, f"--dispatcher --port {port_val}")
    graceful_start_mock.assert_called_once_with(
        "dispatcher", "mock", "mock", "mock", port_val, False
    )
    set_config_mock.assert_called_once_with(
        {
            "dispatcher.address": "0.0.0.0",
            "dispatcher.port": port_val,
        }
    )

    runner = CliRunner()
    port_val = 42
    graceful_start_mock = mocker.patch(
        "covalent_dispatcher._cli.service._graceful_start", return_value=port_val
    )
    set_config_mock = mocker.patch("covalent_dispatcher._cli.service.set_config")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_SRVDIR", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_PIDFILE", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_LOGFILE", "mock")

    runner.invoke(start, f"--ui --ui-port {port_val} -d")
    graceful_start_mock.assert_called_once_with("UI", "mock", "mock", "mock", port_val, True)
    set_config_mock.assert_called_once_with(
        {
            "user_interface.address": "0.0.0.0",
            "user_interface.port": port_val,
        }
    )


def test_stop(mocker, monkeypatch):
    """Test the stop CLI command."""

    runner = CliRunner()
    graceful_shutdown_mock = mocker.patch("covalent_dispatcher._cli.service._graceful_shutdown")
    monkeypatch.setattr("covalent_dispatcher._cli.service.DISPATCHER_PIDFILE", "mock")
    runner.invoke(stop, "--dispatcher")
    graceful_shutdown_mock.assert_called_once_with("dispatcher", "mock")

    runner = CliRunner()
    graceful_shutdown_mock = mocker.patch("covalent_dispatcher._cli.service._graceful_shutdown")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_PIDFILE", "mock")
    runner.invoke(stop, "--ui")
    graceful_shutdown_mock.assert_called_once_with("UI", "mock")


def test_restart():
    pass


def test_status(mocker, monkeypatch):
    """Test covalent status command."""

    pass


def test_is_dispatcher_running(mocker):
    """Test the dispatcher server status checking function."""

    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=1)
    assert _is_dispatcher_running()

    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=-1)
    assert not _is_dispatcher_running()


def test_is_ui_running(mocker):
    """Test the user interface server status checking function."""

    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=1)
    assert _is_ui_running()

    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=-1)
    assert not _is_ui_running()


def test_purge(mocker):
    """Test the 'covalent purge' CLI command."""

    from covalent_dispatcher._cli.service import DISPATCHER_PIDFILE, UI_PIDFILE, get_config

    runner = CliRunner()
    graceful_shutdown_mock = mocker.patch("covalent_dispatcher._cli.service._graceful_shutdown")
    shutil_rmtree_mock = mocker.patch("covalent_dispatcher._cli.service.shutil.rmtree")
    purge_config_mock = mocker.patch("covalent_dispatcher._cli.service.cm.purge_config")
    result = runner.invoke(purge)
    graceful_shutdown_mock.assert_has_calls(
        [mock.call("dispatcher", DISPATCHER_PIDFILE), mock.call("UI", UI_PIDFILE)]
    )
    shutil_rmtree_mock.assert_has_calls(
        [
            mock.call(get_config("sdk.log_dir"), ignore_errors=True),
            mock.call(get_config("dispatcher.cache_dir"), ignore_errors=True),
            mock.call(get_config("dispatcher.log_dir"), ignore_errors=True),
            mock.call(get_config("user_interface.log_dir"), ignore_errors=True),
        ]
    )
    purge_config_mock.assert_called_once()
    assert result.output == "Covalent server files have been purged.\n"
