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

"""Tests for abstract notify endpoint class."""

from covalent.notify.notify import NotifyEndpoint


def test_notify_base_class(mocker):
    mock_notify = mocker.patch("covalent.notify.notify.NotifyEndpoint.notify", return_value=None)

    class MockEndpoint(NotifyEndpoint):
        def notify(self, message: str) -> None:
            super().notify(message)

    endpoint = MockEndpoint()
    endpoint.notify("test message")

    mock_notify.assert_called_once_with("test message")
