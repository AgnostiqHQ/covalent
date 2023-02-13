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

from http.client import HTTPMessage
from unittest.mock import ANY, Mock, call

import pytest

from covalent._results_manager import wait
from covalent._results_manager.results_manager import _get_result_from_dispatcher
from covalent._shared_files.config import get_config

DISPATCH_ID = "91c3ee18-5f2d-44ee-ac2a-39b79cf56646"


@pytest.mark.parametrize(
    "dispatcher_addr",
    [
        "http://" + get_config("dispatcher.address") + ":" + str(get_config("dispatcher.port")),
        "http://localhost:48008",
    ],
)
def test_get_result_from_dispatcher(mocker, dispatcher_addr):
    retries = 10
    getconn_mock = mocker.patch("urllib3.connectionpool.HTTPConnectionPool._get_conn")
    mocker.patch("requests.Response.json", return_value=True)
    headers = HTTPMessage()
    headers.add_header("Retry-After", "2")

    mock_response = [Mock(status=503, msg=headers)] * (retries - 1)
    mock_response.append(Mock(status=200, msg=HTTPMessage()))
    getconn_mock.return_value.getresponse.side_effect = mock_response
    dispatch_id = "9d1b308b-4763-4990-ae7f-6a6e36d35893"
    _get_result_from_dispatcher(
        dispatch_id, wait=wait.LONG, dispatcher_addr=dispatcher_addr, status_only=False
    )
    assert (
        getconn_mock.return_value.request.mock_calls
        == [
            call(
                "GET",
                f"/api/result/{dispatch_id}?wait=True&status_only=False",
                body=None,
                headers=ANY,
            ),
        ]
        * retries
    )
