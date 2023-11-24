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

import pytest

import covalent as ct
from covalent._programmatic.commands import _MISSING_SERVER_WARNING


def test_is_covalent_running(mocker):
    """Check that `is_covalent_running` returns True when the server is running."""
    try:
        from covalent_dispatcher._cli.service import _read_pid  # nopycln: import
    except ModuleNotFoundError:
        pytest.xfail("`covalent_dispatcher` not installed")

    # Simulate server running
    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=1)
    mocker.patch("psutil.pid_exists", return_value=True)
    mocker.patch(
        "covalent._shared_files.config.get_config",
        return_value={"port": 48008, "host": "localhost"},
    )
    assert ct.is_covalent_running()

    # Simulate server stopped
    mocker.patch("covalent_dispatcher._cli.service._read_pid", return_value=-1)
    assert not ct.is_covalent_running()


def test_is_covalent_running_import_error(mocker):
    """Check that `is_covalent_running` catches the `ModuleNotFoundError`."""
    try:
        from covalent_dispatcher._cli.service import _read_pid  # nopycln: import
    except ModuleNotFoundError:
        pytest.xfail("`covalent_dispatcher` not installed")

    mocker.patch(
        "covalent_dispatcher._cli.service._read_pid",
        side_effect=ModuleNotFoundError(),
    )

    mock_app_log = mocker.patch("covalent._programmatic.commands.app_log")

    assert not ct.is_covalent_running()
    mock_app_log.warning.assert_called_once_with(_MISSING_SERVER_WARNING)


def test_covalent_start(mocker):
    """Test the `covalent_start` function without actually starting server."""

    mocker.patch("subprocess.run")

    # Simulate server running
    mocker.patch(
        "covalent._programmatic.commands.is_covalent_running",
        return_value=True,
    )
    ct.covalent_start()

    # Simulate server stopped
    mocker.patch(
        "covalent._programmatic.commands.is_covalent_running",
        return_value=False,
    )
    ct.covalent_start()


def test_covalent_start_quiet(mocker):
    """Test the `covalent_start` function without actually starting server."""

    mocker.patch("subprocess.run")

    # Simulate server running
    mocker.patch(
        "covalent._programmatic.commands.is_covalent_running",
        return_value=True,
    )
    ct.covalent_start(quiet=True)

    # Simulate server stopped
    mocker.patch(
        "covalent._programmatic.commands.is_covalent_running",
        return_value=False,
    )
    ct.covalent_start(quiet=True)


def test_covalent_stop(mocker):
    """Test the `covalent_start` function without actually starting server."""

    mocker.patch("subprocess.run")

    # Simulate server running
    mocker.patch(
        "covalent._programmatic.commands.is_covalent_running",
        return_value=True,
    )
    ct.covalent_stop()

    # Simulate server stopped
    mocker.patch(
        "covalent._programmatic.commands.is_covalent_running",
        return_value=False,
    )
    ct.covalent_stop()


def test_covalent_stop_quiet(mocker):
    """Test the `covalent_start` function without actually starting server."""

    mocker.patch("subprocess.run")

    # Simulate server running
    mocker.patch(
        "covalent._programmatic.commands.is_covalent_running",
        return_value=True,
    )
    ct.covalent_stop(quiet=True)

    # Simulate server stopped
    mocker.patch(
        "covalent._programmatic.commands.is_covalent_running",
        return_value=False,
    )
    ct.covalent_stop(quiet=True)
