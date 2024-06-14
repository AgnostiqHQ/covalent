# Copyright 2023 Agnostiq Inc.
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


"""Unit tests for local module in dispatcher_plugins."""

import tempfile
from unittest.mock import MagicMock

import pytest
from requests import Response
from requests.exceptions import ConnectionError, HTTPError

import covalent as ct
from covalent._dispatcher_plugins.local import LocalDispatcher, get_redispatch_request_body_v2
from covalent._results_manager.result import Result
from covalent._shared_files.utils import format_server_url


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


def test_dispatch_when_no_server_is_running(mocker):
    """test dispatching a lattice when no server is running"""

    # the test suite is using another port, thus, with the dummy address below
    # the covalent server is not running in some sense.
    dummy_dispatcher_addr = "http://localhost:12345"
    endpoint = "/api/v2/dispatches"
    url = dummy_dispatcher_addr + endpoint
    message = f"The Covalent server cannot be reached at {url}. Local servers can be started using `covalent start` in the terminal. If you are using a remote Covalent server, contact your systems administrator to report an outage."

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    mock_print = mocker.patch("covalent._api.apiclient.print")

    with pytest.raises(ConnectionError):
        LocalDispatcher.dispatch(workflow, dispatcher_addr=dummy_dispatcher_addr)(1, 2)

    mock_print.assert_called_once_with(message)


def test_dispatcher_dispatch_multi(mocker):
    """test dispatching a lattice with multistage api"""

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    dispatch_id = "test_dispatcher_dispatch_multi"
    # multistage = True
    mocker.patch("covalent._shared_files.config.get_config", return_value=True)

    mock_register_callable = MagicMock(return_value=dispatch_id)
    mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.register",
        return_value=mock_register_callable,
    )

    mock_reg_tr = mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.register_triggers"
    )
    mock_start = mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.start", return_value=dispatch_id
    )

    assert dispatch_id == LocalDispatcher.dispatch(workflow)(1, 2)

    mock_register_callable.assert_called()
    mock_start.assert_called()


def test_dispatcher_dispatch_with_triggers(mocker):
    """test dispatching a lattice with triggers"""

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    dispatch_id = "test_dispatcher_dispatch_with_triggers"

    workflow.metadata["triggers"] = {"dir_trigger": {}}

    mock_register_callable = MagicMock(return_value=dispatch_id)
    mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.register",
        return_value=mock_register_callable,
    )

    mock_reg_tr = mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.register_triggers"
    )
    mock_start = mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.start", return_value=dispatch_id
    )

    assert dispatch_id == LocalDispatcher.dispatch(workflow)(1, 2)
    mock_reg_tr.assert_called()
    mock_start.assert_not_called()


def test_dispatcher_start(mocker):
    """Test starting a dispatch"""

    dispatch_id = "test_dispatcher_start"
    r = Response()
    r.status_code = 404
    r.url = "http://dummy"
    r.reason = "dummy reason"

    mocker.patch("covalent._api.apiclient.requests.Session.put", return_value=r)

    with pytest.raises(HTTPError, match="404 Client Error: dummy reason for url: http://dummy"):
        LocalDispatcher.start(dispatch_id)

    # test when api doesn't raise an implicit error
    r = Response()
    r.status_code = 202
    r.url = "http://dummy"
    r._content = dispatch_id.encode("utf-8")

    mocker.patch("covalent._api.apiclient.requests.Session.put", return_value=r)

    assert LocalDispatcher.start(dispatch_id) == dispatch_id


def test_register(mocker):
    """test dispatching a lattice with register api"""

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    workflow.build_graph(1, 2)
    with tempfile.TemporaryDirectory() as staging_dir:
        manifest = LocalDispatcher.prepare_manifest(workflow, staging_dir)

    manifest.metadata.dispatch_id = "test_register"

    mock_upload = mocker.patch("covalent._dispatcher_plugins.local.LocalDispatcher.upload_assets")
    mock_prepare_manifest = mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.prepare_manifest",
        return_value=manifest,
    )
    mock_register_manifest = mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.register_manifest"
    )

    dispatch_id = LocalDispatcher.register(workflow)(1, 2)
    assert dispatch_id == "test_register"
    mock_upload.assert_called()


def test_redispatch(mocker):
    """test redispatching a lattice with register api"""

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    workflow.build_graph(1, 2)
    with tempfile.TemporaryDirectory() as staging_dir:
        manifest = LocalDispatcher.prepare_manifest(workflow, staging_dir)

    dispatch_id = "test_register_redispatch"
    manifest.metadata.dispatch_id = dispatch_id
    parent_id = "parent_dispatch_id"

    mock_upload = mocker.patch("covalent._dispatcher_plugins.local.LocalDispatcher.upload_assets")
    mock_get_redispatch_manifest = mocker.patch(
        "covalent._dispatcher_plugins.local.get_redispatch_request_body_v2", return_value=manifest
    )
    mock_register_derived_manifest = mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.register_derived_manifest"
    )
    mock_start = mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.start",
        return_value="test_register_redispatch",
    )

    new_args = (1, 2)
    new_kwargs = {}
    redispatch_id = LocalDispatcher.redispatch(
        dispatch_id=parent_id, replace_electrons={"f": "callable"}, reuse_previous_results=False
    )(*new_args, **new_kwargs)

    assert dispatch_id == redispatch_id
    mock_upload.assert_called()

    mock_start.assert_called_with(dispatch_id, format_server_url())


def test_register_manifest(mocker):
    """Test registering a dispatch manifest."""

    dispatch_id = "test_register_manifest"

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    workflow.build_graph(1, 2)
    with tempfile.TemporaryDirectory() as staging_dir:
        manifest = LocalDispatcher.prepare_manifest(workflow, staging_dir)

    manifest.metadata.dispatch_id = dispatch_id

    r = Response()
    r.status_code = 201
    r.json = MagicMock(return_value=manifest.dict())

    mocker.patch("covalent._api.apiclient.requests.Session.post", return_value=r)

    mock_merge = mocker.patch(
        "covalent._dispatcher_plugins.local.merge_response_manifest", return_value=manifest
    )

    return_manifest = LocalDispatcher.register_manifest(manifest)
    assert return_manifest.metadata.dispatch_id == dispatch_id
    mock_merge.assert_called_with(manifest, manifest)


def test_register_derived_manifest(mocker):
    """Test registering a redispatch manifest."""

    dispatch_id = "test_register_derived_manifest"

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    workflow.build_graph(1, 2)
    with tempfile.TemporaryDirectory() as staging_dir:
        manifest = LocalDispatcher.prepare_manifest(workflow, staging_dir)

    manifest.metadata.dispatch_id = dispatch_id

    r = Response()
    r.status_code = 201
    r.json = MagicMock(return_value=manifest.dict())

    mocker.patch("covalent._api.apiclient.requests.Session.post", return_value=r)

    mock_merge = mocker.patch(
        "covalent._dispatcher_plugins.local.merge_response_manifest", return_value=manifest
    )

    return_manifest = LocalDispatcher.register_derived_manifest(manifest, "original_dispatch")
    assert return_manifest.metadata.dispatch_id == dispatch_id
    mock_merge.assert_called_with(manifest, manifest)


def test_upload_assets(mocker):
    """Test uploading assets to HTTP endpoints"""

    dispatch_id = "test_upload_assets_http"

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    workflow.build_graph(1, 2)
    with tempfile.TemporaryDirectory() as staging_dir:
        manifest = LocalDispatcher.prepare_manifest(workflow, staging_dir)

        num_assets = 0
        # Populate the lattice asset schemas with dummy URLs
        for key, asset in manifest.lattice.assets:
            if asset.size == 0:
                continue
            num_assets += 1
            asset.remote_uri = (
                f"http://localhost:48008/api/v2/dispatches/{dispatch_id}/lattice/assets/dummy"
            )

        endpoint = f"/api/v2/dispatches/{dispatch_id}/lattice/assets/dummy"
        r = Response()
        r.status_code = 200
        mock_put = mocker.patch("covalent._api.apiclient.requests.Session.put", return_value=r)

        LocalDispatcher.upload_assets(manifest)

        assert mock_put.call_count == num_assets


def test_get_redispatch_request_body_norebuild(mocker):
    """Test constructing the request body for redispatch"""

    # Consider the case where the dispatch is to be retried with no
    # changes to inputs or electrons.

    dispatch_id = "test_get_redispatch_request_body_norebuild"

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    workflow.build_graph(1, 2)

    # "Old" result object
    res_obj = Result(workflow)

    # Mock result manager
    mock_resmgr = MagicMock()

    with tempfile.TemporaryDirectory() as staging_dir:
        manifest = LocalDispatcher.prepare_manifest(workflow, staging_dir)
        mock_resmgr._manifest = manifest
        mock_resmgr.result_object = res_obj

        mock_serialize = mocker.patch(
            "covalent._dispatcher_plugins.local.serialize_result", return_value=manifest
        )
        mocker.patch(
            "covalent._dispatcher_plugins.local.ResultSchema.parse_obj", return_value=manifest
        )
        mocker.patch(
            "covalent._dispatcher_plugins.local.get_result_manager", return_value=mock_resmgr
        )

    with tempfile.TemporaryDirectory() as redispatch_dir:
        redispatch_manifest = get_redispatch_request_body_v2(
            dispatch_id, redispatch_dir, [], {}, replace_electrons={}
        )

        assert redispatch_manifest is manifest


def test_get_redispatch_request_body_replace_electrons(mocker):
    """Test constructing the request body for redispatch"""

    # Consider the case where electrons are to be replaced but lattice
    # inputs stay the same.

    dispatch_id = "test_get_redispatch_request_body_replace_electrons"

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.electron
    def new_task(a, b, c):
        return a * b * c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    workflow.build_graph(1, 2)

    # "Old" result object
    res_obj = Result(workflow)

    # Mock result manager
    mock_resmgr = MagicMock()

    with tempfile.TemporaryDirectory() as staging_dir:
        manifest = LocalDispatcher.prepare_manifest(workflow, staging_dir)
        mock_resmgr._manifest = manifest
        mock_resmgr.result_object = res_obj

        mock_serialize = mocker.patch(
            "covalent._dispatcher_plugins.local.serialize_result", return_value=manifest
        )
        mocker.patch(
            "covalent._dispatcher_plugins.local.ResultSchema.parse_obj", return_value=manifest
        )
        mocker.patch(
            "covalent._dispatcher_plugins.local.get_result_manager", return_value=mock_resmgr
        )

    with tempfile.TemporaryDirectory() as redispatch_dir:
        redispatch_manifest = get_redispatch_request_body_v2(
            dispatch_id, redispatch_dir, [], {}, replace_electrons={"task": new_task}
        )

        assert redispatch_manifest is manifest
        mock_resmgr.download_lattice_asset.assert_any_call("workflow_function")
        mock_resmgr.download_lattice_asset.assert_any_call("workflow_function_string")
        mock_resmgr.download_lattice_asset.assert_any_call("inputs")

        mock_resmgr.load_lattice_asset.assert_any_call("workflow_function")
        mock_resmgr.load_lattice_asset.assert_any_call("workflow_function_string")
        mock_resmgr.load_lattice_asset.assert_any_call("inputs")


def test_get_redispatch_request_body_replace_inputs(mocker):
    """Test constructing the request body for redispatch"""

    # Consider the case where only lattice
    # inputs are changed.

    dispatch_id = "test_get_redispatch_request_body_replace_inputs"

    @ct.electron
    def task(a, b, c):
        return a + b + c

    @ct.lattice
    def workflow(a, b):
        return task(a, b, c=4)

    workflow.build_graph(1, 2)

    # "Old" result object
    res_obj = Result(workflow)

    # Mock result manager
    mock_resmgr = MagicMock()

    with tempfile.TemporaryDirectory() as staging_dir:
        manifest = LocalDispatcher.prepare_manifest(workflow, staging_dir)
        mock_resmgr._manifest = manifest
        mock_resmgr.result_object = res_obj

        mock_serialize = mocker.patch(
            "covalent._dispatcher_plugins.local.serialize_result", return_value=manifest
        )
        mocker.patch(
            "covalent._dispatcher_plugins.local.ResultSchema.parse_obj", return_value=manifest
        )
        mocker.patch(
            "covalent._dispatcher_plugins.local.get_result_manager", return_value=mock_resmgr
        )

    with tempfile.TemporaryDirectory() as redispatch_dir:
        redispatch_manifest = get_redispatch_request_body_v2(
            dispatch_id, redispatch_dir, [3, 4], {}, replace_electrons=None
        )

        assert redispatch_manifest is manifest
        mock_resmgr.download_lattice_asset.assert_any_call("workflow_function")
        mock_resmgr.download_lattice_asset.assert_any_call("workflow_function_string")

        mock_resmgr.load_lattice_asset.assert_any_call("workflow_function")
        mock_resmgr.load_lattice_asset.assert_any_call("workflow_function_string")
