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

import tempfile
from unittest.mock import Mock

import mock
import pytest
from click.testing import CliRunner
from psutil import pid_exists

from covalent._data_store.datastore import DataStore
from covalent_dispatcher._cli.service import (
    MIGRATION_COMMAND_MSG,
    MIGRATION_WARNING_MSG,
    _graceful_shutdown,
    _graceful_start,
    _is_server_running,
    _next_available_port,
    _port_from_pid,
    _read_pid,
    _rm_pid_file,
    cluster,
    purge,
    restart,
    start,
    status,
    stop,
)

STOPPED_SERVER_STATUS_ECHO = "Covalent server is stopped.\n"
RUNNING_SERVER_STATUS_ECHO = "Covalent server is running at http://localhost:42.\n"


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
        "covalent_dispatcher._cli.service.get_config", return_value=1984
    )
    click_echo_mock = mocker.patch("click.echo")
    res = _graceful_start("", "", "", 15, False)
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

    with mock.patch("covalent_dispatcher._cli.service.open", mock.mock_open()):
        res = _graceful_start("", "", "output.log", 15, False)
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

    _graceful_shutdown(pidfile="mock")

    click_echo_mock.assert_called_once_with("Covalent server has stopped.")
    rm_pid_file_mock.assert_called_once_with("mock")
    read_pid_mock.assert_called_once()
    assert process_mock.called


def test_graceful_shutdown_stopped_server(mocker):
    """Test the graceful shutdown functionality."""

    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=12)
    mocker.patch("psutil.pid_exists", return_value=False)
    process_mock = mocker.patch("psutil.Process")
    rm_pid_file_mock = mocker.patch("covalent_dispatcher._cli.service._rm_pid_file")
    click_echo_mock = mocker.patch("click.echo")

    _graceful_shutdown(pidfile="mock")

    click_echo_mock.assert_called_once_with("Covalent server was not running.")
    rm_pid_file_mock.assert_called_once_with("mock")
    assert not process_mock.called


@pytest.mark.parametrize(
    "is_migration_pending, ignore_migrations",
    [(True, True), (True, False), (False, False), (False, True)],
)
def test_start(mocker, monkeypatch, is_migration_pending, ignore_migrations):
    """Test the start CLI command."""

    runner = CliRunner()
    port_val = 42

    graceful_start_mock = mocker.patch(
        "covalent_dispatcher._cli.service._graceful_start", return_value=port_val
    )
    db_mock = Mock()
    mocker.patch.object(DataStore, "factory", lambda: db_mock)
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_SRVDIR", "mock")
    set_config_mock = mocker.patch("covalent_dispatcher._cli.service.set_config")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_SRVDIR", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_PIDFILE", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_LOGFILE", "mock")

    db_mock.is_migration_pending = is_migration_pending

    cli_args = f"--port {port_val} -d"

    if ignore_migrations:
        cli_args = f"{cli_args} --ignore-migrations"

    res = runner.invoke(start, cli_args)

    if ignore_migrations or not is_migration_pending:
        graceful_start_mock.assert_called_once()
        set_config_mock.assert_called()
    else:
        assert MIGRATION_COMMAND_MSG in res.output
        assert MIGRATION_WARNING_MSG in res.output
        assert res.exit_code == 1


def test_stop(mocker, monkeypatch):
    """Test the stop CLI command."""

    runner = CliRunner()
    graceful_shutdown_mock = mocker.patch("covalent_dispatcher._cli.service._graceful_shutdown")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_PIDFILE", "mock")
    runner.invoke(stop)
    graceful_shutdown_mock.assert_called_once_with("mock")


@pytest.mark.parametrize(
    "port_tag,port,server,pid,restart_called,start_called,stop_called",
    [
        ("port", 42, "ui", -1, False, True, True),
        ("port", 42, "ui", 100, True, True, True),
    ],
)
def test_restart(mocker, port_tag, port, pid, server, restart_called, start_called, stop_called):
    """Test the restart CLI command."""

    start = mocker.patch("covalent_dispatcher._cli.service.start")
    stop = mocker.patch("covalent_dispatcher._cli.service.stop")
    mocker.patch("covalent_dispatcher._cli.service.get_config", return_value=port)

    obj = mocker.MagicMock()
    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=pid)

    runner = CliRunner()
    runner.invoke(restart, f"--{port_tag} {port}", obj=obj)
    assert start.called is start_called
    assert stop.called is stop_called


@pytest.mark.parametrize(
    "port_val,pid,echo_output,file_removed,pid_exists",
    [
        (None, -1, STOPPED_SERVER_STATUS_ECHO, True, False),
        (42, 42, RUNNING_SERVER_STATUS_ECHO, False, True),
        (42, 42, STOPPED_SERVER_STATUS_ECHO, True, False),
    ],
)
def test_status(mocker, port_val, pid, echo_output, file_removed, pid_exists):
    """Test covalent status command."""

    mocker.patch("covalent_dispatcher._cli.service.get_config", return_value=port_val)
    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=pid)
    mocker.patch("psutil.pid_exists", return_value=pid_exists)
    rm_pid_file_mock = mocker.patch("covalent_dispatcher._cli.service._rm_pid_file")

    runner = CliRunner()
    res = runner.invoke(status)

    assert res.output == echo_output
    assert rm_pid_file_mock.called is file_removed


def test_is_server_running(mocker):
    """Test the server status checking function."""

    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=1)
    assert _is_server_running()

    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=-1)
    assert not _is_server_running()


def test_purge(mocker):
    """Test the 'covalent purge' CLI command."""

    from covalent_dispatcher._cli.service import UI_PIDFILE, get_config

    runner = CliRunner()
    graceful_shutdown_mock = mocker.patch("covalent_dispatcher._cli.service._graceful_shutdown")
    shutil_rmtree_mock = mocker.patch("covalent_dispatcher._cli.service.shutil.rmtree")
    purge_config_mock = mocker.patch("covalent_dispatcher._cli.service.cm.purge_config")
    result = runner.invoke(purge)
    graceful_shutdown_mock.assert_has_calls([mock.call(UI_PIDFILE)])
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


@pytest.mark.parametrize("workers", [1, 2, 3, 4])
def test_cluster_size(mocker, workers):
    """
    Test to ensure that cluster start with the expected number of workers
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = workers

    click = mock.Mock()
    click.echo = lambda: workers

    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_size_mock = mocker.patch(
        "covalent_dispatcher._cli.service._get_cluster_size", return_value=workers
    )

    runner = CliRunner()
    response = runner.invoke(cluster, "--size")

    assert get_config_mock.call_count == 2
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_size_mock.assert_called_once()
    assert int(response.output) == workers


def test_cluster_info(mocker):
    """
    Test cluster info CLI
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = lambda: ""

    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_info_cli_mock = mocker.patch("covalent_dispatcher._cli.service._get_cluster_info")
    click_echo_mock = mocker.patch("covalent_dispatcher._cli.service.click.echo")

    runner = CliRunner()
    _ = runner.invoke(cluster, "--info")

    assert get_config_mock.call_count == 2
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_info_cli_mock.assert_called_once()
    click_echo_mock.assert_called_once()


def test_cluster_status_cli(mocker):
    """
    Test cluster status cli
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = lambda: ""

    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_status_cli_mock = mocker.patch("covalent_dispatcher._cli.service._get_cluster_status")
    click_echo_mock = mocker.patch("covalent_dispatcher._cli.service.click.echo")

    runner = CliRunner()
    _ = runner.invoke(cluster, "--status")

    assert get_config_mock.call_count == 2
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_status_cli_mock.assert_called_once()
    click_echo_mock.assert_called_once()


def test_cluster_address_cli(mocker):
    """
    Test cluster address cli
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = lambda: ""

    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_cli_mock = mocker.patch("covalent_dispatcher._cli.service._get_cluster_address")
    click_echo_mock = mocker.patch("covalent_dispatcher._cli.service.click.echo")

    runner = CliRunner()
    _ = runner.invoke(cluster, "--address")

    assert get_config_mock.call_count == 2
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_cli_mock.assert_called_once()
    click_echo_mock.assert_called_once()


def test_cluster_logs_cli(mocker):
    """
    Test cluster logs cli
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = lambda: ""

    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_cli_mock = mocker.patch("covalent_dispatcher._cli.service._get_cluster_logs")
    click_echo_mock = mocker.patch("covalent_dispatcher._cli.service.click.echo")

    runner = CliRunner()
    _ = runner.invoke(cluster, "--logs")

    assert get_config_mock.call_count == 2
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_cli_mock.assert_called_once()
    click_echo_mock.assert_called_once()


def test_cluster_restart_cli(mocker):
    """
    Test cluster restart cli
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = lambda: ""

    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_cli_mock = mocker.patch("covalent_dispatcher._cli.service._cluster_restart")
    click_echo_mock = mocker.patch("covalent_dispatcher._cli.service.click.echo")

    runner = CliRunner()
    _ = runner.invoke(cluster, "--restart")

    assert get_config_mock.call_count == 2
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_cli_mock.assert_called_once()
    click_echo_mock.assert_called_once()


def test_cluster_scale_cli(mocker):
    """
    Test cluster scale cli
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = lambda: ""

    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_cli_mock = mocker.patch("covalent_dispatcher._cli.service._cluster_scale")
    click_echo_mock = mocker.patch("covalent_dispatcher._cli.service.click.echo")

    runner = CliRunner()
    _ = runner.invoke(cluster, "--scale 1")

    assert get_config_mock.call_count == 2
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_cli_mock.assert_called_once()
    click_echo_mock.assert_called_once()
