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

from unittest.mock import call

import pytest
import requests

import covalent as ct
from covalent._results_manager.result import Result
from covalent._shared_files.interface import _poll_result, _retrieve_result_response, sync


@ct.electron
def sample_task():
    return 5


@ct.lattice
def sample_lattice():
    return sample_task()


@pytest.fixture
def ok_response():
    response = requests.Response()
    response.status_code = 200
    response._content = "ok"

    return response


def test_retrieve_result_response(mocker, ok_response):
    route_mock = mocker.patch(
        "covalent._shared_files.get_svc_uri.ResultsURI.get_route", return_value="svc_route"
    )
    session_get_mock = mocker.patch("requests.Session.get", return_value=ok_response)
    raise_mock = mocker.patch("requests.Response.raise_for_status", return_value="ok")

    session = requests.Session()
    response = _retrieve_result_response(session, "dispatch-id")
    assert response == ok_response

    route_mock.assert_called_once_with("workflow/results/dispatch-id")
    session_get_mock.assert_called_once_with("svc_route", stream=True)
    raise_mock.assert_called_once_with()


@pytest.mark.parametrize("wait", [True, False])
def test_poll_result(mocker, ok_response, wait):
    retrieve_result_mock = mocker.patch(
        "covalent._shared_files.interface._retrieve_result_response", return_value=ok_response
    )

    result_mock = Result(sample_lattice, "", "dispatch-id")
    result_mock._status = Result.COMPLETED

    session_mock = mocker.patch("requests.Session", return_value="session")
    session = requests.Session()

    pickle_load_mock = mocker.patch(
        "covalent._shared_files.interface.pickle.loads", return_value=result_mock
    )

    response = _poll_result(session, "dispatch-id", wait)
    assert response == ok_response

    retrieve_result_mock.assert_called_once_with(session, "dispatch-id")
    if wait:
        pickle_load_mock.assert_called_once_with("ok")
    else:
        pickle_load_mock.assert_not_called()


@pytest.mark.parametrize(
    "dispatch_id", ["sample-dispatch-id", ["sample-dispatch-1", "sample-dispatch-2"]]
)
def test_sync(mocker, dispatch_id):
    session_mock = mocker.patch("requests.Session", return_value="session")
    poll_mock = mocker.patch("covalent._shared_files.interface._poll_result")

    sync(dispatch_id)

    session_mock.assert_called_once_with()
    if isinstance(dispatch_id, str):
        poll_mock.assert_called_once_with("session", dispatch_id, True)
    elif isinstance(dispatch_id, list):
        poll_mock.assert_has_calls(
            [
                call("session", "sample-dispatch-1", True),
                call("session", "sample-dispatch-2", True),
            ]
        )
    else:
        assert False
