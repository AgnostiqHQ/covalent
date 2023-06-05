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
from requests import Response
from requests.exceptions import HTTPError

import covalent as ct
from covalent._dispatcher_plugins.local import LocalDispatcher


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
        match="The Covalent dispatcher server cannot be reached",
    ):
        LocalDispatcher.dispatch(workflow, dispatcher_addr=dummy_dispatcher_addr)(1, 2)


def test_dispatcher_submit_api(mocker):
    """test dispatching a lattice with submit api"""

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    # test when api raises an implicit error
    r = Response()
    r.status_code = 404
    r.url = "http://dummy"
    r.reason = "dummy reason"

    mocker.patch("covalent._api.apiclient.requests.post", return_value=r)

    with pytest.raises(HTTPError, match="404 Client Error: dummy reason for url: http://dummy"):
        dispatch_id = LocalDispatcher.dispatch(workflow)(1, 2)
        assert dispatch_id is None

    # test when api doesn't raise an implicit error
    r = Response()
    r.status_code = 201
    r.url = "http://dummy"
    r._content = b"abcde"

    mocker.patch("covalent._api.apiclient.requests.post", return_value=r)

    dispatch_id = LocalDispatcher.dispatch(workflow)(1, 2)
    assert dispatch_id == "abcde"
