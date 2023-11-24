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
from covalent._programmatic.commands import WARNING_MSG


def test_covalent_start_and_stop(mocker):
    """Test that `covalent_start` successfully starts a local Covalent Server"""

    def _flipping_retval():
        retval = _flipping_retval.state
        _flipping_retval.state = not _flipping_retval.state
        return retval

    # Disable server actions in test environment
    mocker.patch("click.Context.invoke", return_value=None)

    # Assumer server is not running
    is_covalent_running_patch = mocker.patch(
        "covalent._programmatic.commands.is_covalent_running",
    )
    is_covalent_running_patch.side_effect = _flipping_retval

    # Since `is_covalent_running` is called at least twice in both start and stop:
    # once to check check status and again to check for change in status.

    # Start Covalent as if not running.
    _flipping_retval.state = False
    ct.covalent_start(quiet=True)

    # Re-issue start command as if already running.
    _flipping_retval.state = True
    ct.covalent_start(quiet=True)

    # Stop Covalent as if running.
    _flipping_retval.state = True
    ct.covalent_stop(quiet=True)

    # Re-issue stop command as if already stopped.
    _flipping_retval.state = False
    ct.covalent_stop(quiet=True)


def test_covalent_start_and_stop_timeouts(mocker):
    """Test that `covalent_start` successfully starts a local Covalent Server"""

    # Disable server actions in test environment
    mocker.patch("click.Context.invoke", return_value=None)

    # Make timeout shorter for testing
    mocker.patch("covalent._programmatic.commands._TIMEOUT", 0.1)

    # Assumer server is not running
    is_covalent_running_patch = mocker.patch(
        "covalent._programmatic.commands.is_covalent_running",
    )

    is_covalent_running_patch.return_value = False
    with pytest.raises(TimeoutError):
        ct.covalent_start(quiet=True)

    is_covalent_running_patch.return_value = True
    with pytest.raises(TimeoutError):
        ct.covalent_stop(quiet=True)


def test_covalent_start_import_error(mocker):
    """Test that `covalent_start` shows a warning if covalent_dispatcher is not installed"""

    mocker.patch("click.Context.invoke", return_value=None)

    mock_app_log_warning = mocker.patch("covalent._programmatic.commands.app_log.warning")

    mocker.patch(
        "covalent._programmatic.commands.is_covalent_running",
        side_effect=ImportError,
    )

    ct.covalent_start(quiet=True)
    mock_app_log_warning.assert_called_once_with(WARNING_MSG)


def test_covalent_stop_import_error(mocker):
    """Test that `covalent_stop` shows a warning if covalent_dispatcher is not installed"""

    mocker.patch("click.Context.invoke", return_value=None)

    mock_app_log_warning = mocker.patch("covalent._programmatic.commands.app_log.warning")

    mocker.patch(
        "covalent._programmatic.commands.is_covalent_running",
        side_effect=ImportError,
    )

    ct.covalent_stop(quiet=True)
    mock_app_log_warning.assert_called_once_with(WARNING_MSG)


def test_is_covalent_running():
    """Test that the `is_covalent_running` function agrees with the CLI status check"""

    from covalent_dispatcher._cli import _is_server_running

    # TODO: Seems we can't start/stop the server in the test environment.
    # Check here is not complete, but at least it is necessary.
    assert ct.is_covalent_running() == _is_server_running()


def test_is_covalent_running_import_error(mocker):
    """Test that `is_covalent_running` returns False if covalent_dispatcher is not installed"""

    mock_app_log_warning = mocker.patch("covalent._programmatic.commands.app_log.warning")

    # _read_pid isn't importable
    mocker.patch(
        "covalent_dispatcher._cli.service._read_pid",
        side_effect=ImportError,
    )

    assert not ct.is_covalent_running()
    mock_app_log_warning.assert_called_once_with(WARNING_MSG)
