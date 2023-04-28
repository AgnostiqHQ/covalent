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

from unittest.mock import MagicMock

import pytest
from requests import Response
from requests.exceptions import HTTPError

import covalent as ct
from covalent._dispatcher_plugins.local import LocalDispatcher, get_redispatch_request_body


def test_get_redispatch_request_body_null_arguments():
    """Test the get request body function with null arguments."""

    @ct.electron
    def identity(a):
        return a

    @ct.electron
    def add(a, b):
        return a + b

    response = get_redispatch_request_body(
        "mock-dispatch-id",
    )
    assert response == {
        "json_lattice": None,
        "dispatch_id": "mock-dispatch-id",
        "electron_updates": {},
        "reuse_previous_results": False,
    }


def test_get_redispatch_request_body_args_kwargs(mocker):
    """Test the get request body function when args/kwargs is not null."""
    mock_electron = MagicMock()
    get_result_mock = mocker.patch("covalent._dispatcher_plugins.local.get_result")
    get_result_mock().lattice.serialize_to_json.return_value = "mock-json-lattice"

    response = get_redispatch_request_body(
        "mock-dispatch-id",
        new_args=[1, 2],
        new_kwargs={"a": 1, "b": 2},
        replace_electrons={"mock-task-id": mock_electron},
    )
    assert response == {
        "json_lattice": "mock-json-lattice",
        "dispatch_id": "mock-dispatch-id",
        "electron_updates": {"mock-task-id": mock_electron.electron_object.as_transportable_dict},
        "reuse_previous_results": False,
    }
    get_result_mock().lattice.build_graph.assert_called_once_with(*[1, 2], **{"a": 1, "b": 2})


@pytest.mark.parametrize("is_pending", [True, False])
@pytest.mark.parametrize(
    "replace_electrons,expected_arg",
    [(None, {}), ({"mock-electron-1": "mock-electron-2"}, {"mock-electron-1": "mock-electron-2"})],
)
def test_redispatch(mocker, replace_electrons, expected_arg, is_pending):
    """Test the local re-dispatch function."""

    mocker.patch("covalent._dispatcher_plugins.local.get_config", return_value="mock-config")
    requests_mock = mocker.patch("covalent._dispatcher_plugins.local.requests")
    get_request_body_mock = mocker.patch(
        "covalent._dispatcher_plugins.local.get_redispatch_request_body",
        return_value={"mock-request-body"},
    )

    local_dispatcher = LocalDispatcher()
    func = local_dispatcher.redispatch(
        "mock-dispatch-id", replace_electrons=replace_electrons, is_pending=is_pending
    )
    func()
    requests_mock.post.assert_called_once_with(
        "http://mock-config:mock-config/api/redispatch",
        json={"mock-request-body"},
        params={"is_pending": is_pending},
    )
    requests_mock.post().raise_for_status.assert_called_once()
    requests_mock.post().content.decode().strip().replace.assert_called_once_with('"', "")

    get_request_body_mock.assert_called_once_with("mock-dispatch-id", (), {}, expected_arg, False)


def test_dispatching_a_non_lattice():
    """test dispatching a non-lattice"""

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.electron
    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    with pytest.raises(
        TypeError, match="Dispatcher expected a Lattice, received <class 'function'> instead."
    ):
        LocalDispatcher.dispatch(workflow)(1, 2)


def test_dispatch_when_no_server_is_running():
    """test dispatching a lattice when no server is running"""

    # the test suite is using another port, thus, with the dummy address below
    # the covalent server is not running in some sense.
    dummy_dispatcher_addr = "http://localhost:12345"

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    with pytest.raises(
        ConnectionError,
        match=f"The Covalent dispatcher server is not running at {dummy_dispatcher_addr}.",
    ):
        LocalDispatcher.dispatch(workflow, dispatcher_addr=dummy_dispatcher_addr)(1, 2)


def test_dispatcher_submit_api_raise_for_status(mocker):
    """test dispatching a lattice when submit api raises an error"""

    def patched_post(url, data=None, json=None, **kwargs):
        r = Response()
        r.status_code = 404
        r.url = "http://dummy"
        r.reason = "dummy reason"
        return r

    mocker.patch("covalent._dispatcher_plugins.local.requests.post", side_effect=patched_post)

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    with pytest.raises(HTTPError, match="404 Client Error: dummy reason for url: http://dummy"):
        dispatch_id = LocalDispatcher.dispatch(workflow)(1, 2)
        assert dispatch_id is None
