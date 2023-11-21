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


def test_covalent_start_and_stop():
    """Test that `covalent_start` successfully starts a local Covalent Server"""

    import requests

    from covalent_dispatcher._cli import _is_server_running

    # Start Covalent
    ct.covalent_start(quiet=True)
    assert _is_server_running() is True

    # Re-issue start command (should do nothing and exit immediately)
    ct.covalent_start(quiet=True)
    assert _is_server_running() is True

    # Run a dummy workflow
    @ct.lattice
    @ct.electron
    def dummy_1():
        return "success"

    dispatch_id = ct.dispatch(dummy_1)()
    assert ct.get_result(dispatch_id, wait=True).result == "success"

    # Stop Covalent
    ct.covalent_stop(quiet=True)
    assert _is_server_running() is False

    # Re-issue stop command (should do nothing and exit immediately)
    ct.covalent_stop(quiet=True)
    assert _is_server_running() is False

    # Try running the dummy workflow again (should fail)
    with pytest.raises(requests.exceptions.ConnectionError):
        ct.dispatch(dummy_1)()

    # Re-start Covalent after stopping
    ct.covalent_start(quiet=False)
    assert _is_server_running() is True

    # Run another dummy workflow
    @ct.lattice
    @ct.electron
    def dummy_2():
        return "success again"

    dispatch_id = ct.dispatch(dummy_2)()
    assert ct.get_result(dispatch_id, wait=True).result == "success again"

    # Finally, stop Covalent
    ct.covalent_stop(quiet=False)
    assert _is_server_running() is False


def test_covalent_is_running():
    """Test that the `covalent_is_running` function agrees with the CLI status check"""

    from covalent_dispatcher._cli import _is_server_running

    # Start Covalent
    ct.covalent_start(quiet=True)
    assert ct.covalent_is_running() is _is_server_running() is True

    # Stop Covalent
    ct.covalent_stop(quiet=True)
    assert ct.covalent_is_running() is _is_server_running() is False
