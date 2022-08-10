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
from unittest import result
from unittest.mock import ANY, Mock, call

import pytest

from covalent._data_store.models import Lattice
from covalent._results_manager import wait
from covalent._results_manager.results_manager import _get_result_from_dispatcher, result_from
from covalent._shared_files.config import get_config


@pytest.fixture
def lattice_record():
    return Lattice(
        id=1,
        dispatch_id="mock_dispatch_id",
        name="mock_name",
        status="mock_status",
        electron_num="mock_electron_num",
        completed_electron_num="mock_completed_electron_num",
        storage_type="local",
        storage_path="mock_storage_path",
        function_filename="mock_function_filename",
        function_string_filename="mock_function_string_filename",
        executor_data_filename="mock_executor_data_filename",
        error_filename="mock_error_filename",
        inputs_filename="mock_inputs_filename",
        results_filename="mock_results_filename",
        transport_graph_filename="mock_transport_graph_filename",
        is_active=True,
        created_at=None,
        updated_at=None,
        started_at=None,
        completed_at=None,
    )


def test_result_from(lattice_record, mocker):
    """Test the method to rehydrate a result object from a lattice record."""

    mock_load_file = mocker.patch("covalent._results_manager.results_manager.load_file")
    result_from(lattice_record)
    mock_load_file.assert_called()


def test_get_result_from_dispatcher(mocker):
    retries = 10
    getconn_mock = mocker.patch("urllib3.connectionpool.HTTPConnectionPool._get_conn")
    mocker.patch("requests.Response.json", return_value=True)
    headers = HTTPMessage()
    headers.add_header("Retry-After", "2")

    mock_response = [Mock(status=503, msg=headers)] * (retries - 1)
    mock_response.append(Mock(status=200, msg=HTTPMessage()))
    getconn_mock.return_value.getresponse.side_effect = mock_response
    dispatch_id = "9d1b308b-4763-4990-ae7f-6a6e36d35893"
    dispatcher = get_config("dispatcher.address") + ":" + str(get_config("dispatcher.port"))
    _get_result_from_dispatcher(
        dispatch_id, wait=wait.LONG, dispatcher=dispatcher, status_only=False
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
