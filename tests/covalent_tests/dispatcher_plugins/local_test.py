# Copyright 2023 Agnostiq Inc.
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


"""Unit tests for local module in dispatcher_plugins."""

import pytest

from covalent._dispatcher_plugins.local import LocalDispatcher


@pytest.mark.parametrize(
    "replace_electrons,expected_arg",
    [(None, {}), ({"mock-electron-1": "mock-electron-2"}, {"mock-electron-1": "mock-electron-2"})],
)
def test_redispatch(mocker, replace_electrons, expected_arg):
    """Test the local re-dispatch function."""

    mocker.patch("covalent._dispatcher_plugins.local.get_config", return_value="mock-config")
    requests_mock = mocker.patch("covalent._dispatcher_plugins.local.requests")
    get_request_body_mock = mocker.patch(
        "covalent._dispatcher_plugins.local.get_request_body", return_value={"mock-request-body"}
    )

    local_dispatcher = LocalDispatcher()
    func = local_dispatcher.redispatch("mock-dispatch-id", replace_electrons=replace_electrons)
    func()
    requests_mock.post.assert_called_once_with(
        "http://mock-config:mock-config/api/redispatch", json={"mock-request-body"}
    )
    requests_mock.post().raise_for_status.assert_called_once()
    requests_mock.post().content.decode().strip().replace.assert_called_once_with('"', "")

    get_request_body_mock.assert_called_once_with("mock-dispatch-id", (), {}, expected_arg, False)
