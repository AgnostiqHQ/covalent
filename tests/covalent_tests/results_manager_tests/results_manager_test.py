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

"""Tests for results manager."""


from covalent._results_manager.results_manager import cancel


def test_cancel_with_single_task_id(mocker):
    mock_request_post = mocker.patch(
        "covalent._api.apiclient.requests.Session.post",
    )

    cancel(dispatch_id="dispatch", task_ids=1)

    mock_request_post.assert_called_once()
    mock_request_post.return_value.raise_for_status.assert_called_once()


def test_cancel_with_multiple_task_ids(mocker):
    mock_task_ids = [0, 1]

    mock_request_post = mocker.patch(
        "covalent._api.apiclient.requests.Session.post",
    )

    cancel(dispatch_id="dispatch", task_ids=[1, 2, 3])

    mock_request_post.assert_called_once()
    mock_request_post.return_value.raise_for_status.assert_called_once()
