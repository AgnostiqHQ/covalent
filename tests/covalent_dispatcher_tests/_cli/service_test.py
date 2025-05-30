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

"""Tests for Covalent command line interface (CLI) Tool."""

import os
import signal
import subprocess
import sys
import tempfile
import venv
from unittest import mock
from unittest.mock import MagicMock, Mock, call

import psutil
import pytest
import requests
from click.testing import CliRunner

from covalent_dispatcher._cli.service import (
    MIGRATION_COMMAND_MSG,
    MIGRATION_WARNING_MSG,
    STOPPED_PROCESS_STATUS_MSG,
    ZOMBIE_PROCESS_STATUS_MSG,
    _graceful_shutdown,
    _graceful_start,
    _is_server_running,
    _next_available_port,
    _port_from_pid,
    _read_pid,
    _rm_pid_file,
    cluster,
    config,
    get_config,
    logs,
    purge,
    restart,
    start,
    status,
    stop,
)
from covalent_dispatcher._db.datastore import DataStore

STOPPED_SERVER_STATUS_ECHO = "Covalent server is stopped.\n"
RUNNING_SERVER_STATUS_ECHO = "Covalent server is running at http://localhost:42.\n"
STOPPED_PROCESS_STATUS_ECHO = STOPPED_PROCESS_STATUS_MSG + "\n"
ZOMBIE_PROCESS_STATUS_ECHO = ZOMBIE_PROCESS_STATUS_MSG + "\n"


def has_conda():
    try:
        ret = subprocess.run(["conda"], check=True)
        return ret.returncode == 0
    except FileNotFoundError:
        return False


def conda_test(f):
    mark = pytest.mark.conda
    skip = pytest.mark.skipif(not has_conda(), reason="conda is unavailable")
    return mark(skip(f))


@conda_test
def test_python_path_in_conda_env():
    with tempfile.TemporaryDirectory() as tmp_dir:
        create_cmd = ["conda", "create", "-y", "--prefix", tmp_dir, "python=3.9.12"]
        subprocess.run(create_cmd, check=True)
        check_path_cmd = [
            "conda",
            "run",
            "--prefix",
            tmp_dir,
            "python",
            "-c",
            "import sys; print(sys.executable)",
        ]
        res = subprocess.run(check_path_cmd, check=True, capture_output=True)
        assert res.stdout.decode().startswith(tmp_dir)
        check_version_cmd = ["conda", "run", "--prefix", tmp_dir, "python", "--version"]
        res = subprocess.run(check_version_cmd, check=True, capture_output=True)
        assert res.stdout.decode().strip() == "Python 3.9.12"


def test_python_path_in_venv():
    with tempfile.TemporaryDirectory() as tmp_dir:
        venv.create(tmp_dir, with_pip=False)
        custom_env = os.environ.copy()
        # equivalent of source venv/bin/activate
        custom_env["VIRTUAL_ENV"] = os.path.realpath(tmp_dir)
        custom_env["PATH"] = f"{tmp_dir}/bin:$PATH"
        check_path_cmd = [
            "python",
            "-c",
            "import os; import sys; print(os.path.realpath(sys.executable))",
        ]
        res = subprocess.run(check_path_cmd, check=True, capture_output=True, env=custom_env)
        assert res.stdout.decode().startswith(os.path.realpath(tmp_dir))


def test_read_pid_nonexistent_file():
    """Test the process id read function when the pid file does not exist."""

    with tempfile.TemporaryDirectory() as tmp_dir:
        assert _read_pid(f"{tmp_dir}/nonexistent.pid") == -1


def test_read_valid_pid_file():
    """Test the process id read function when the pid file exists."""

    with mock.patch("covalent_dispatcher._cli.service.open", mock.mock_open(read_data="1984")):
        res = _read_pid(filename="mock.pid")
    assert res == 1984


@pytest.mark.parametrize("file_exists, remove_call_status", [(False, False), (True, True)])
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

    read_pid_mock.assert_called_once()
    pid_exists_mock.assert_called_once()
    port_from_pid_mock.assert_called_once()


@pytest.mark.parametrize("no_triggers_flag", [True, False])
@pytest.mark.parametrize("triggers_only_flag", [True, False])
def test_graceful_start_when_pid_absent(monkeypatch, mocker, no_triggers_flag, triggers_only_flag):
    """Test the graceful server start function."""

    config_paths = [
        "dispatcher.cache_dir",
        "dispatcher.results_dir",
        "dispatcher.log_dir",
        "user_interface.log_dir",
    ]

    def patched_fn(entry):
        return entry

    tmp_dir = tempfile.TemporaryDirectory()
    monkeypatch.setenv("COVALENT_CONFIG_DIR", tmp_dir.name)

    read_pid_mock = mocker.patch("covalent_dispatcher._cli.service._read_pid")
    pid_exists_mock = mocker.patch("psutil.pid_exists", return_value=False)
    rm_pid_file_mock = mocker.patch("covalent_dispatcher._cli.service._rm_pid_file")
    next_available_port_mock = mocker.patch(
        "covalent_dispatcher._cli.service._next_available_port", return_value=1984
    )
    popen_mock = mocker.patch("covalent_dispatcher._cli.service.Popen")
    click_echo_mock = mocker.patch("click.echo")
    requests_mock = mocker.patch(
        "covalent_dispatcher._cli.service.requests.get",
    )

    no_triggers_str = "--no-triggers" if no_triggers_flag else ""
    triggers_only_str = "--triggers-only" if triggers_only_flag else ""

    launch_str = f" {sys.executable} app.py  --port 1984  {no_triggers_str} {triggers_only_str}>> output.log 2>&1"

    with mock.patch("covalent_dispatcher._cli.service.open", mock.mock_open()):
        if no_triggers_flag and triggers_only_flag:
            with pytest.raises(ValueError) as ve:
                res = _graceful_start(
                    "", "", "output.log", 15, False, False, no_triggers_flag, triggers_only_flag
                )
        else:
            res = _graceful_start(
                "", "", "output.log", 15, False, False, no_triggers_flag, triggers_only_flag
            )
            assert res == 1984

            for each_path in config_paths:
                path = get_config(each_path)
                assert os.path.exists(path)

            popen_mock.assert_called_once()
            assert popen_mock.call_args[0][0] == launch_str

            next_available_port_mock.assert_called_once()

    rm_pid_file_mock.assert_called_once()
    pid_exists_mock.assert_called_once()
    read_pid_mock.assert_called_once()


def test_graceful_start_waits_to_return(mocker):
    """Check that graceful server start function doesn't return until
    the endpoints are live."""

    read_pid_mock = mocker.patch("covalent_dispatcher._cli.service._read_pid")
    pid_exists_mock = mocker.patch("psutil.pid_exists", return_value=False)
    rm_pid_file_mock = mocker.patch("covalent_dispatcher._cli.service._rm_pid_file")
    next_available_port_mock = mocker.patch(
        "covalent_dispatcher._cli.service._next_available_port", return_value=1984
    )
    popen_mock = mocker.patch("covalent_dispatcher._cli.service.Popen")
    click_echo_mock = mocker.patch("click.echo")
    requests_mock = mocker.patch(
        "covalent_dispatcher._cli.service.requests.get",
        side_effect=requests.exceptions.ConnectionError(),
    )
    sleep_mock = mocker.patch(
        "covalent_dispatcher._cli.service.time.sleep", side_effect=RuntimeError()
    )

    with mock.patch("covalent_dispatcher._cli.service.open", mock.mock_open()):
        with pytest.raises(RuntimeError):
            res = _graceful_start("", "", "output.log", 15, False)

    sleep_mock.assert_called_once()


def test_graceful_shutdown_running_server(mocker):
    """Test the graceful shutdown functionality."""

    read_pid_mock = mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=12)
    mocker.patch("psutil.pid_exists", return_value=True)
    process_mock = mocker.patch("psutil.Process")
    rm_pid_file_mock = mocker.patch("covalent_dispatcher._cli.service._rm_pid_file")
    click_echo_mock = mocker.patch("click.echo")

    _graceful_shutdown(pidfile="mock")

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

    rm_pid_file_mock.assert_called_once_with("mock")
    assert not process_mock.called


@pytest.mark.parametrize("is_migration_pending", [True, False])
@pytest.mark.parametrize("ignore_migrations", [True, False])
@pytest.mark.parametrize("current_revision", [None, "112233"])
def test_start(mocker, monkeypatch, is_migration_pending, ignore_migrations, current_revision):
    """Test the start CLI command."""

    runner = CliRunner()
    port_val = 42

    graceful_start_mock = mocker.patch(
        "covalent_dispatcher._cli.service._graceful_start", return_value=port_val
    )
    db_mock = Mock()
    mocker.patch.object(DataStore, "factory", lambda: db_mock)
    set_config_mock = mocker.patch("covalent_dispatcher._cli.service.set_config")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_SRVDIR", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_PIDFILE", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_LOGFILE", "mock")

    db_mock.is_migration_pending = is_migration_pending
    db_mock.current_revision.return_value = current_revision

    cli_args = f"--port {port_val} -d"

    if ignore_migrations:
        cli_args = f"{cli_args} --ignore-migrations"

    res = runner.invoke(start, cli_args)

    # if current_revision is None no migrations have been run
    if current_revision is None and not ignore_migrations:
        db_mock.current_revision.assert_called_once()

    if ignore_migrations or not is_migration_pending:
        graceful_start_mock.assert_called_once()
        assert set_config_mock.call_count == 6
    else:
        assert MIGRATION_COMMAND_MSG in res.output.replace("\n", "")
        assert MIGRATION_WARNING_MSG in res.output.replace("\n", "")
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

    mock_config_map = {
        "user_interface.port": port,
        "sdk.log_level": "debug",
        "sdk.no_cluster": "true",
        "dask.mem_per_worker": 1024,
        "dask.threads_per_worker": 2,
        "dask.num_workers": 4,
    }

    def mock_config(key):
        return mock_config_map[key]

    start = mocker.patch("covalent_dispatcher._cli.service.start")
    stop = mocker.patch("covalent_dispatcher._cli.service.stop")
    mocker.patch("covalent_dispatcher._cli.service.get_config", mock_config)

    obj = mocker.MagicMock()
    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=pid)

    runner = CliRunner()
    runner.invoke(restart, f"--{port_tag} {port}", obj=obj)
    assert start.called is start_called
    assert stop.called is stop_called


@pytest.mark.parametrize(
    "port_tag,port,pid,server,no_cluster",
    [
        ("port", 42, 100, "ui", "true"),
        ("port", 42, 100, "ui", "false"),
    ],
)
def test_restart_preserves_nocluster(mocker, port_tag, port, pid, server, no_cluster):
    """Test the restart CLI command preserves the setting of sdk.no_cluster."""

    mock_config_map = {
        "user_interface.port": port,
        "sdk.log_level": "debug",
        "sdk.no_cluster": no_cluster,
        "dask.mem_per_worker": 1024,
        "dask.threads_per_worker": 2,
        "dask.num_workers": 4,
    }
    no_cluster_map = {"true": True, "false": False}

    def mock_config(key):
        return mock_config_map[key]

    start = mocker.patch("covalent_dispatcher._cli.service.start")
    stop = mocker.patch("covalent_dispatcher._cli.service.stop")
    mocker.patch("covalent_dispatcher._cli.service.get_config", mock_config)

    obj = mocker.MagicMock()
    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=pid)

    configuration = {
        "port": mock_config_map["user_interface.port"],
        "develop": (mock_config_map["sdk.log_level"] == "debug"),
        "no_cluster": no_cluster_map[mock_config_map["sdk.no_cluster"]],
        "mem_per_worker": mock_config_map["dask.mem_per_worker"],
        "threads_per_worker": mock_config_map["dask.threads_per_worker"],
        "workers": mock_config_map["dask.num_workers"],
        "no_header": True,
    }
    runner = CliRunner()
    runner.invoke(restart, f"--{port_tag} {port}", obj=obj)
    start.assert_called_with(**configuration)


@pytest.mark.parametrize(
    "port_val,pid,echo_output,file_removed,pid_exists,process_status",
    [
        (None, -1, "Stopped", True, False, None),
        (42, 42, "Running", False, True, psutil.STATUS_RUNNING),
        (42, 42, "Stopped", True, False, None),
        (42, 42, "Stopped", False, True, psutil.STATUS_ZOMBIE),
        (42, 42, "Stopped", False, True, psutil.STATUS_STOPPED),
    ],
)
def test_status(mocker, port_val, pid, echo_output, file_removed, pid_exists, process_status):
    """Test covalent status command."""

    mocker.patch("covalent_dispatcher._cli.service.get_config", return_value=port_val)
    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=pid)
    mocker.patch("psutil.pid_exists", return_value=pid_exists)
    mocker.patch("psutil.Process.status", return_value=process_status)
    rm_pid_file_mock = mocker.patch("covalent_dispatcher._cli.service._rm_pid_file")
    process_mock = Mock(spec=psutil.Process)
    process_mock.status.return_value = process_status
    with mocker.patch("psutil.Process", return_value=process_mock):
        runner = CliRunner()
        res = runner.invoke(status)

        assert rm_pid_file_mock.called is file_removed


def test_is_server_running(mocker):
    """Test the server status checking function."""

    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=1)
    assert _is_server_running()

    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=-1)
    assert not _is_server_running()


@pytest.mark.parametrize("hard", [False, True])
def test_purge_proceed(hard, mocker):
    """Test the 'covalent purge' CLI command."""

    from covalent_dispatcher._cli.service import UI_PIDFILE

    runner = CliRunner()

    dir_list = [
        mock.call(dirs)
        for dirs in [
            "sdk.log_dir",
            "dispatcher.cache_dir",
            "dispatcher.log_dir",
            "user_interface.log_dir",
        ]
    ]

    def get_config_side_effect(conf_name):
        return "file" if conf_name == "dispatcher.db_path" else "dir"

    get_config_mock = mocker.patch(
        "covalent_dispatcher._cli.service.get_config", side_effect=get_config_side_effect
    )
    os_path_dirname_mock = mocker.patch(
        "covalent_dispatcher._cli.service.os.path.dirname", return_value="dir"
    )

    def isdir_side_effect(path):
        return path == "dir"

    os_path_isdir_mock = mocker.patch(
        "covalent_dispatcher._cli.service.os.path.isdir", side_effect=isdir_side_effect
    )

    graceful_shutdown_mock = mocker.patch("covalent_dispatcher._cli.service._graceful_shutdown")
    shutil_rmtree_mock = mocker.patch("covalent_dispatcher._cli.service.shutil.rmtree")
    os_remove_mock = mocker.patch("covalent_dispatcher._cli.service.os.remove")

    if hard:
        result = runner.invoke(purge, args="--hard", input="y")

        dir_list.append(mock.call("dispatcher.db_path"))
        os_path_isdir_mock.assert_has_calls([mock.call("file"), mock.call("file")], any_order=True)
        os_remove_mock.assert_called_with("file")
        assert get_config_mock.call_count == 5
    else:
        result = runner.invoke(purge, input="y")

        assert get_config_mock.call_count == 4
        get_config_mock.assert_has_calls(dir_list, any_order=True)
        assert os_path_dirname_mock.call_count == 1
        os_path_isdir_mock.assert_has_calls([mock.call("dir"), mock.call("dir")], any_order=True)

    graceful_shutdown_mock.assert_called_with(UI_PIDFILE)

    shutil_rmtree_mock.assert_has_calls([mock.call("dir", ignore_errors=True)])


@pytest.mark.parametrize("hard", [False, True])
def test_purge_abort(hard, mocker):
    """Test the 'covalent purge' CLI command."""

    runner = CliRunner()

    dir_list = [
        mock.call(dirs)
        for dirs in [
            "sdk.log_dir",
            "dispatcher.cache_dir",
            "dispatcher.log_dir",
            "user_interface.log_dir",
        ]
    ]

    def get_config_side_effect(conf_name):
        return "file" if conf_name == "dispatcher.db_path" else "dir"

    get_config_mock = mocker.patch(
        "covalent_dispatcher._cli.service.get_config", side_effect=get_config_side_effect
    )
    os_path_dirname_mock = mocker.patch(
        "covalent_dispatcher._cli.service.os.path.dirname", return_value="dir"
    )

    def isdir_side_effect(path):
        return path == "dir"

    os_path_isdir_mock = mocker.patch(
        "covalent_dispatcher._cli.service.os.path.isdir", side_effect=isdir_side_effect
    )

    if hard:
        result = runner.invoke(purge, input="n", args="--hard")
        dir_list.append(mock.call("dispatcher.db_path"))
        os_path_isdir_mock.assert_has_calls([mock.call("file")])
    else:
        result = runner.invoke(purge, input="n")

    get_config_mock.assert_has_calls(dir_list, any_order=True)
    assert os_path_dirname_mock.call_count == 1
    os_path_isdir_mock.assert_has_calls([mock.call("dir")])

    assert "aborted" in result.output


@pytest.mark.parametrize("exists", [False, True])
def test_logs(exists, mocker):
    """Test covalent logs command"""

    from covalent_dispatcher._cli.service import UI_LOGFILE

    runner = CliRunner()

    mocker.patch("covalent_dispatcher._cli.service.os.path.exists", return_value=exists)

    if not exists:
        result = runner.invoke(logs)
        assert result.output.startswith(UI_LOGFILE)
    else:
        m_open = mock.mock_open(read_data="testing")
        with mock.patch("covalent_dispatcher._cli.service.open", m_open):
            result = runner.invoke(logs)

        m_open.assert_called_once_with(UI_LOGFILE, "r")
        assert "testing" in result.output


def test_config(mocker):
    """Test covalent config cli"""

    cfg_read_config_mock = mocker.patch(
        "covalent_dispatcher._cli.service.ConfigManager.read_config"
    )
    json_dumps_mock = mocker.patch("covalent_dispatcher._cli.service.json.dumps")
    click_echo_mock = mocker.patch("covalent_dispatcher._cli.service.click.echo")

    runner = CliRunner()
    runner.invoke(config)

    cfg_read_config_mock.assert_called_once()
    json_dumps_mock.assert_called_once()


@pytest.mark.parametrize("workers", [1, 2, 3, 4])
def test_cluster_size(mocker, workers):
    """
    Test to ensure that cluster start with the expected number of workers
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = workers

    click = mock.Mock()
    click.echo = lambda: workers

    is_server_running_mock = mocker.patch(
        "covalent_dispatcher._cli.service._is_server_running", return_value=True
    )
    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    is_server_running_mock = mocker.patch(
        "covalent_dispatcher._cli.service._is_server_running", return_value=True
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_size_mock = mocker.patch(
        "covalent_dispatcher._cli.service._get_cluster_size", return_value=workers
    )

    runner = CliRunner()
    response = runner.invoke(cluster, "--size")

    is_server_running_mock.assert_called_once()
    assert is_server_running_mock.return_value
    assert get_config_mock.call_count == 2
    is_server_running_mock.assert_called_once()
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_size_mock.assert_called_once()
    assert str(workers) in response.output


def test_cluster_info(mocker):
    """
    Test cluster info CLI
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = lambda: ""

    is_server_running_mock = mocker.patch(
        "covalent_dispatcher._cli.service._is_server_running", return_value=True
    )
    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    is_server_running_mock = mocker.patch(
        "covalent_dispatcher._cli.service._is_server_running", return_value=True
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_info_cli_mock = mocker.patch("covalent_dispatcher._cli.service._get_cluster_info")
    click_echo_mock = mocker.patch("covalent_dispatcher._cli.service.click.echo")
    json_dumps_mock = mocker.patch("covalent_dispatcher._cli.service.json.dumps")

    runner = CliRunner()
    _ = runner.invoke(cluster, "--info")

    is_server_running_mock.assert_called_once()
    assert is_server_running_mock.return_value
    assert get_config_mock.call_count == 2
    is_server_running_mock.assert_called_once()
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_info_cli_mock.assert_called_once()


def test_cluster_status_cli(mocker):
    """
    Test cluster status cli
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = lambda: ""

    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    is_server_running_mock = mocker.patch(
        "covalent_dispatcher._cli.service._is_server_running", return_value=True
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_status_cli_mock = mocker.patch("covalent_dispatcher._cli.service._get_cluster_status")
    click_echo_mock = mocker.patch("covalent_dispatcher._cli.service.click.echo")
    json_dumps_mock = mocker.patch("covalent_dispatcher._cli.service.json.dumps")

    runner = CliRunner()
    _ = runner.invoke(cluster, "--status")

    is_server_running_mock.assert_called_once()
    assert is_server_running_mock.return_value
    assert get_config_mock.call_count == 2
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_status_cli_mock.assert_called_once()


def test_cluster_address_cli(mocker):
    """
    Test cluster address cli
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = lambda: ""

    is_server_running_mock = mocker.patch(
        "covalent_dispatcher._cli.service._is_server_running", return_value=True
    )
    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    is_server_running_mock = mocker.patch(
        "covalent_dispatcher._cli.service._is_server_running", return_value=True
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_cli_mock = mocker.patch("covalent_dispatcher._cli.service._get_cluster_address")
    click_echo_mock = mocker.patch("covalent_dispatcher._cli.service.click.echo")
    json_dumps_mock = mocker.patch("covalent_dispatcher._cli.service.json.dumps")

    runner = CliRunner()
    _ = runner.invoke(cluster, "--address")

    is_server_running_mock.assert_called_once()
    assert is_server_running_mock.return_value
    assert get_config_mock.call_count == 2
    is_server_running_mock.assert_called_once()
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_cli_mock.assert_called_once()


def test_cluster_logs_cli(mocker):
    """
    Test cluster logs cli
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = lambda: ""

    is_server_running_mock = mocker.patch(
        "covalent_dispatcher._cli.service._is_server_running", return_value=True
    )
    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    is_server_running_mock = mocker.patch(
        "covalent_dispatcher._cli.service._is_server_running", return_value=True
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_cli_mock = mocker.patch("covalent_dispatcher._cli.service._get_cluster_logs")
    click_echo_mock = mocker.patch("covalent_dispatcher._cli.service.click.echo")
    json_dumps_mock = mocker.patch("covalent_dispatcher._cli.service.json.dumps")

    runner = CliRunner()
    _ = runner.invoke(cluster, "--logs")

    is_server_running_mock.assert_called_once()
    assert is_server_running_mock.return_value
    assert get_config_mock.call_count == 2
    is_server_running_mock.assert_called_once()
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_cli_mock.assert_called_once()


def test_cluster_restart_cli(mocker):
    """
    Test cluster restart cli
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = lambda: ""

    is_server_running_mock = mocker.patch(
        "covalent_dispatcher._cli.service._is_server_running", return_value=True
    )
    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    is_server_running_mock = mocker.patch(
        "covalent_dispatcher._cli.service._is_server_running", return_value=True
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_cli_mock = mocker.patch("covalent_dispatcher._cli.service._cluster_restart")
    click_echo_mock = mocker.patch("covalent_dispatcher._cli.service.click.echo")

    runner = CliRunner()
    _ = runner.invoke(cluster, "--restart")

    is_server_running_mock.assert_called_once()
    assert is_server_running_mock.return_value
    assert get_config_mock.call_count == 2
    is_server_running_mock.assert_called_once()
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_cli_mock.assert_called_once()


def test_cluster_scale_cli(mocker):
    """
    Test cluster scale cli
    """

    loop = mock.Mock()
    loop.run_until_complete.return_value = lambda: ""

    is_server_running_mock = mocker.patch(
        "covalent_dispatcher._cli.service._is_server_running", return_value=True
    )
    get_event_loop_mock = mocker.patch(
        "covalent_dispatcher._cli.service.asyncio.get_event_loop", return_value=loop
    )
    is_server_running_mock = mocker.patch(
        "covalent_dispatcher._cli.service._is_server_running", return_value=True
    )
    get_config_mock = mocker.patch("covalent_dispatcher._cli.service.get_config")
    unparse_addr_mock = mocker.patch("covalent_dispatcher._cli.service.unparse_address")
    cluster_cli_mock = mocker.patch("covalent_dispatcher._cli.service._cluster_scale")
    click_echo_mock = mocker.patch("covalent_dispatcher._cli.service.click.echo")

    runner = CliRunner()
    _ = runner.invoke(cluster, "--scale 1")

    is_server_running_mock.assert_called_once()
    assert is_server_running_mock.return_value
    assert get_config_mock.call_count == 2
    is_server_running_mock.assert_called_once()
    get_event_loop_mock.assert_called_once()
    unparse_addr_mock.assert_called_once()
    cluster_cli_mock.assert_called_once()


def test_start_config_mem_per_worker(mocker, monkeypatch):
    """Test setting mem_per_worker"""
    runner = CliRunner()
    port_val = 42

    graceful_start_mock = mocker.patch(
        "covalent_dispatcher._cli.service._graceful_start", return_value=port_val
    )
    db_mock = Mock()
    mocker.patch.object(DataStore, "factory", lambda: db_mock)
    set_config_mock = mocker.patch("covalent_dispatcher._cli.service.set_config")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_SRVDIR", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_PIDFILE", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_LOGFILE", "mock")

    db_mock.is_migration_pending = False

    cli_args = f"--port {port_val} -d --mem-per-worker 1GB"

    res = runner.invoke(start, cli_args)

    assert set_config_mock.call_count == 7
    graceful_start_mock.assert_called_once()


def test_start_config_threads_per_worker(mocker, monkeypatch):
    """Test setting threads_per_worker"""
    runner = CliRunner()
    port_val = 42

    graceful_start_mock = mocker.patch(
        "covalent_dispatcher._cli.service._graceful_start", return_value=port_val
    )
    db_mock = Mock()
    mocker.patch.object(DataStore, "factory", lambda: db_mock)
    set_config_mock = mocker.patch("covalent_dispatcher._cli.service.set_config")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_SRVDIR", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_PIDFILE", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_LOGFILE", "mock")

    db_mock.is_migration_pending = False

    cli_args = f"--port {port_val} -d --threads-per-worker 1"

    res = runner.invoke(start, cli_args)

    assert set_config_mock.call_count == 7
    graceful_start_mock.assert_called_once()


def test_start_config_num_workers(mocker, monkeypatch):
    """Test setting workers"""
    runner = CliRunner()
    port_val = 42

    graceful_start_mock = mocker.patch(
        "covalent_dispatcher._cli.service._graceful_start", return_value=port_val
    )
    db_mock = Mock()
    mocker.patch.object(DataStore, "factory", lambda: db_mock)
    set_config_mock = mocker.patch("covalent_dispatcher._cli.service.set_config")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_SRVDIR", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_PIDFILE", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_LOGFILE", "mock")

    db_mock.is_migration_pending = False

    cli_args = f"--port {port_val} -d --workers 1"

    res = runner.invoke(start, cli_args)

    assert set_config_mock.call_count == 7
    graceful_start_mock.assert_called_once()


def test_start_all_dask_config(mocker, monkeypatch):
    """Test setting all dask configuration options"""
    runner = CliRunner()
    port_val = 42

    graceful_start_mock = mocker.patch(
        "covalent_dispatcher._cli.service._graceful_start", return_value=port_val
    )
    db_mock = Mock()
    mocker.patch.object(DataStore, "factory", lambda: db_mock)
    set_config_mock = mocker.patch("covalent_dispatcher._cli.service.set_config")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_SRVDIR", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_PIDFILE", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_LOGFILE", "mock")

    db_mock.is_migration_pending = False

    cli_args = f"--port {port_val} -d --mem-per-worker 1GB --threads-per-worker 1 --workers 1"

    res = runner.invoke(start, cli_args)

    assert set_config_mock.call_count == 9
    graceful_start_mock.assert_called_once()


def test_start_dask_config_options_workers_and_mem_per_worker(mocker, monkeypatch):
    """Test setting workers and mem-per-worker"""
    runner = CliRunner()
    port_val = 42

    graceful_start_mock = mocker.patch(
        "covalent_dispatcher._cli.service._graceful_start", return_value=port_val
    )
    db_mock = Mock()
    mocker.patch.object(DataStore, "factory", lambda: db_mock)
    set_config_mock = mocker.patch("covalent_dispatcher._cli.service.set_config")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_SRVDIR", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_PIDFILE", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_LOGFILE", "mock")

    db_mock.is_migration_pending = False

    cli_args = f"--port {port_val} -d --mem-per-worker 1GB --workers 1"

    res = runner.invoke(start, cli_args)

    assert set_config_mock.call_count == 8
    graceful_start_mock.assert_called_once()


def test_start_dask_config_options_workers_and_threads_per_worker(mocker, monkeypatch):
    """Test setting workers, threads-per-worker"""
    runner = CliRunner()
    port_val = 42

    graceful_start_mock = mocker.patch(
        "covalent_dispatcher._cli.service._graceful_start", return_value=port_val
    )
    db_mock = Mock()
    mocker.patch.object(DataStore, "factory", lambda: db_mock)
    set_config_mock = mocker.patch("covalent_dispatcher._cli.service.set_config")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_SRVDIR", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_PIDFILE", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_LOGFILE", "mock")

    db_mock.is_migration_pending = False

    cli_args = f"--port {port_val} -d --threads-per-worker 1 --workers 1"

    res = runner.invoke(start, cli_args)

    assert set_config_mock.call_count == 8
    graceful_start_mock.assert_called_once()


def test_start_dask_config_options_mem_per_workers_and_threads_per_worker(mocker, monkeypatch):
    """Test setting mem-per-worker and threads-per-worker"""
    runner = CliRunner()
    port_val = 42

    graceful_start_mock = mocker.patch(
        "covalent_dispatcher._cli.service._graceful_start", return_value=port_val
    )
    db_mock = Mock()
    mocker.patch.object(DataStore, "factory", lambda: db_mock)
    set_config_mock = mocker.patch("covalent_dispatcher._cli.service.set_config")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_SRVDIR", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_PIDFILE", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_LOGFILE", "mock")

    db_mock.is_migration_pending = False

    cli_args = f"--port {port_val} -d --mem-per-worker 1GB --threads-per-worker 1"

    res = runner.invoke(start, cli_args)

    assert set_config_mock.call_count == 8
    graceful_start_mock.assert_called_once()


def test_sdk_no_cluster(mocker, monkeypatch):
    runner = CliRunner()
    port_val = 42

    graceful_start_mock = mocker.patch(
        "covalent_dispatcher._cli.service._graceful_start", return_value=port_val
    )
    db_mock = Mock()
    mocker.patch.object(DataStore, "factory", lambda: db_mock)
    set_config_mock = mocker.patch("covalent_dispatcher._cli.service.set_config")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_SRVDIR", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_PIDFILE", "mock")
    monkeypatch.setattr("covalent_dispatcher._cli.service.UI_LOGFILE", "mock")

    db_mock.is_migration_pending = False

    cli_args = f"--port {port_val} -d --no-cluster"

    res = runner.invoke(start, cli_args)

    assert set_config_mock.call_count == 6
    graceful_start_mock.assert_called_once()


def test_purge_hidden_option(mocker):
    """Test the 'covalent purge' CLI command."""

    from covalent_dispatcher._cli.service import UI_PIDFILE

    runner = CliRunner()

    def get_config_side_effect(conf_name):
        return "file" if conf_name == "dispatcher.db_path" else "dir"

    get_config_mock = mocker.patch(
        "covalent_dispatcher._cli.service.get_config", side_effect=get_config_side_effect
    )
    os_path_dirname_mock = mocker.patch(
        "covalent_dispatcher._cli.service.os.path.dirname", return_value="dir"
    )

    def isdir_side_effect(path):
        return path == "dir"

    os_path_isdir_mock = mocker.patch(
        "covalent_dispatcher._cli.service.os.path.isdir", side_effect=isdir_side_effect
    )

    graceful_shutdown_mock = mocker.patch("covalent_dispatcher._cli.service._graceful_shutdown")
    shutil_rmtree_mock = mocker.patch("covalent_dispatcher._cli.service.shutil.rmtree")
    os_remove_mock = mocker.patch("covalent_dispatcher._cli.service.os.remove")

    result = runner.invoke(purge, args="--hell-yeah")

    os_path_isdir_mock.assert_has_calls(
        [mock.call("dir"), mock.call("file")],
        any_order=True,
    )
    os_remove_mock.assert_called_with("file")
    assert get_config_mock.call_count == 5

    graceful_shutdown_mock.assert_called_with(UI_PIDFILE)

    shutil_rmtree_mock.assert_has_calls([mock.call("dir", ignore_errors=True)])


def test_terminate_child_processes(mocker):
    from covalent_dispatcher._cli.service import _terminate_child_processes

    psutil_process_mock = mocker.patch(
        "covalent_dispatcher._cli.service.psutil.Process", return_value=MagicMock()
    )
    children_mock = MagicMock()
    psutil_process_mock.return_value.children.return_value = [children_mock]
    wait_procs_mock = mocker.patch("covalent_dispatcher._cli.service.psutil.wait_procs")

    _terminate_child_processes(1)

    psutil_process_mock.assert_has_calls(
        [
            call(1),
            call(children_mock.pid),
        ]
    )
    psutil_process_mock.return_value.children.assert_has_calls(
        [
            call(),
            call(recursive=True),
        ]
    )
    children_mock.send_signal.assert_called_once_with(signal.SIGINT)
    children_mock.kill.assert_called_once_with()
    wait_procs_mock.assert_called_once_with([children_mock])
    children_mock.wait.assert_called_once_with()


def test_graceful_start_permission_exception(mocker):
    graceful_start_mock = mocker.patch(
        "covalent_dispatcher._cli.service._graceful_start",
        side_effect=PermissionError("Permission denied"),
    )
    click_secho_mock = mocker.patch("covalent_dispatcher._cli.service.click.secho")

    runner = CliRunner()
    runner.invoke(start)

    graceful_start_mock.assert_called_once()
    assert click_secho_mock.call_count == 3
