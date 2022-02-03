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

import mock
import pytest
from click.testing import CliRunner

from covalent_dispatcher._cli.service import (
    _is_dispatcher_running,
    _is_ui_running,
    _next_available_port,
    _port_from_pid,
    _read_pid,
    _rm_pid_file,
    purge,
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
    with mocker.patch("socket.socket.bind"):
        res = _next_available_port(requested_port=12)
    assert res == 12

    # Case 2 - Next two ports are not available.
    with mocker.patch(
        "socket.socket.bind", side_effect=[Exception("OSERROR"), Exception("OSERROR"), None]
    ):
        res = _next_available_port(requested_port=12)
    assert res == 14


def test_graceful_start():
    pass


def test_graceful_shutdown():
    pass


def test_graceful_restart():
    pass


def test_start():
    pass


def test_stop():
    pass


def test_restart():
    pass


def test_status():
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
