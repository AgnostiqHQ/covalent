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

import os
import tempfile
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from requests import Response

import covalent as ct
from covalent._results_manager.results_manager import (
    MissingLatticeRecordError,
    Result,
    ResultManager,
    _get_result_export_from_dispatcher,
    cancel,
    download_asset,
    get_result,
)
from covalent._serialize.result import serialize_result
from covalent._workflow.transportable_object import TransportableObject


def get_test_manifest(staging_dir):
    @ct.electron
    def identity(x):
        return x

    @ct.electron
    def add(x, y):
        return x + y

    @ct.lattice
    def workflow(x, y):
        res1 = identity(x)
        res2 = identity(y)
        return add(res1, res2)

    workflow.build_graph(2, 3)
    result_object = Result(workflow)
    ts = datetime.now(timezone.utc)
    result_object._start_time = ts
    result_object._end_time = ts
    result_object._result = TransportableObject(42)
    result_object.lattice.transport_graph.set_node_value(0, "status", Result.COMPLETED)
    result_object.lattice.transport_graph.set_node_value(0, "output", TransportableObject(2))
    manifest = serialize_result(result_object, staging_dir)

    # Swap asset uri and remote_uri to simulate an exported manifest
    for key, asset in manifest.assets:
        asset.remote_uri = asset.uri
        asset.uri = None

    for key, asset in manifest.lattice.assets:
        asset.remote_uri = asset.uri
        asset.uri = None

    for node in manifest.lattice.transport_graph.nodes:
        for key, asset in node.assets:
            asset.remote_uri = asset.uri
            asset.uri = None

    return manifest


def test_cancel_with_single_task_id(mocker):
    mock_request_put = mocker.patch(
        "covalent._api.apiclient.requests.Session.put",
    )

    cancel(dispatch_id="dispatch", task_ids=1)

    mock_request_put.assert_called_once()
    mock_request_put.return_value.raise_for_status.assert_called_once()


def test_cancel_with_multiple_task_ids(mocker):
    mock_task_ids = [0, 1]

    mock_request_put = mocker.patch(
        "covalent._api.apiclient.requests.Session.put",
    )

    cancel(dispatch_id="dispatch", task_ids=[1, 2, 3])

    mock_request_put.assert_called_once()
    mock_request_put.return_value.raise_for_status.assert_called_once()


def test_result_export(mocker):
    with tempfile.TemporaryDirectory() as staging_dir:
        test_manifest = get_test_manifest(staging_dir)

    dispatch_id = "test_result_export"

    mock_body = {"id": "test_result_export", "status": "COMPLETED"}

    mock_client = MagicMock()
    mock_response = Response()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value=mock_body)

    # mock_client.get = MagicMock(return_value=mock_response)
    mocker.patch("covalent._api.apiclient.requests.Session.get", return_value=mock_response)

    # mocker.patch(
    #     "covalent._results_manager.results_manager.CovalentAPIClient", return_value=mock_client
    # )

    endpoint = f"/api/v2/dispatches/{dispatch_id}"
    assert mock_body == _get_result_export_from_dispatcher(
        dispatch_id, wait=False, status_only=True
    )


def test_result_manager_assets_local_copies():
    """Test downloading and loading assets using local asset uris."""
    dispatch_id = "test_result_manager"
    with tempfile.TemporaryDirectory() as server_dir:
        # This will have uri and remote_uri swapped so as to simulate
        # a manifest exported from the server. All "downloads" will be
        # local file copies from server_dir to results_dir.
        manifest = get_test_manifest(server_dir)
        with tempfile.TemporaryDirectory() as results_dir:
            rm = ResultManager(manifest, results_dir)
            rm.download_lattice_asset("workflow_function")
            rm.load_lattice_asset("workflow_function")
            rm.download_result_asset("result")
            rm.load_result_asset("result")
            os.makedirs(f"{results_dir}/node_0")
            rm.download_node_asset(0, "output")
            rm.load_node_asset(0, "output")

        res_obj = rm.result_object
        assert res_obj.lattice(3, 5) == 8
        assert res_obj.result == 42

        output = res_obj.lattice.transport_graph.get_node_value(0, "output")
        assert output.get_deserialized() == 2


def test_result_manager_save_manifest():
    """Test saving and loading manifests"""
    dispatch_id = "test_result_manager_save_load"
    with tempfile.TemporaryDirectory() as server_dir:
        # This will have uri and remote_uri swapped so as to simulate
        # a manifest exported from the server. All "downloads" will be
        # local file copies from server_dir to results_dir.
        manifest = get_test_manifest(server_dir)
        with tempfile.TemporaryDirectory() as results_dir:
            rm = ResultManager(manifest, results_dir)
            rm.save()
            path = os.path.join(results_dir, "manifest.json")
            rm2 = ResultManager.load(path, results_dir)
        assert rm2._results_dir == results_dir
        assert rm2._manifest == rm._manifest


def test_get_result(mocker):
    dispatch_id = "test_result_manager"
    with tempfile.TemporaryDirectory() as server_dir:
        # This will have uri and remote_uri swapped so as to simulate
        # a manifest exported from the server. All "downloads" will be
        # local file copies from server_dir to results_dir.
        manifest = get_test_manifest(server_dir)

        mock_result_export = {
            "id": dispatch_id,
            "status": "COMPLETED",
            "result_export": manifest.dict(),
        }
        mocker.patch(
            "covalent._results_manager.results_manager._get_result_export_from_dispatcher",
            return_value=mock_result_export,
        )
        with tempfile.TemporaryDirectory() as results_dir:
            res_obj = get_result(dispatch_id, results_dir=results_dir)

            assert res_obj.result == 42


def test_get_result_sublattice(mocker):
    dispatch_id = "test_result_manager_sublattice"
    sub_dispatch_id = "test_result_manager_sublattice_sub"

    with tempfile.TemporaryDirectory() as server_dir:
        # This will have uri and remote_uri swapped so as to simulate
        # a manifest exported from the server. All "downloads" will be
        # local file copies from server_dir to results_dir.
        manifest = get_test_manifest(server_dir)

        node = manifest.lattice.transport_graph.nodes[0]
        node.metadata.sub_dispatch_id = sub_dispatch_id

        with tempfile.TemporaryDirectory() as server_dir_sub:
            # Sublattice manifest
            sub_manifest = get_test_manifest(server_dir_sub)

            mock_result_export = {
                "id": dispatch_id,
                "status": "COMPLETED",
                "result_export": manifest.dict(),
            }

            mock_subresult_export = {
                "id": sub_dispatch_id,
                "status": "COMPLETED",
                "result_export": sub_manifest.dict(),
            }

            exports = {dispatch_id: mock_result_export, sub_dispatch_id: mock_subresult_export}

            def mock_get_export(dispatch_id, *args, **kwargs):
                return exports[dispatch_id]

            mocker.patch(
                "covalent._results_manager.results_manager._get_result_export_from_dispatcher",
                mock_get_export,
            )
            with tempfile.TemporaryDirectory() as results_dir:
                res_obj = get_result(dispatch_id, results_dir=results_dir)

                assert res_obj.result == 42
                tg = res_obj.lattice.transport_graph
                for node_id in tg._graph.nodes:
                    if node_id == 0:
                        assert tg.get_node_value(node_id, "sub_dispatch_id") == sub_dispatch_id
                        assert tg.get_node_value(node_id, "sublattice_result") is not None

                    else:
                        assert tg.get_node_value(1, "sublattice_result") is None


def test_get_result_404(mocker):
    """Check exception handing for invalid dispatch ids."""

    dispatch_id = "test_get_result_404"
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_client.get = MagicMock(return_value=mock_response)

    mocker.patch(
        "covalent._results_manager.results_manager.CovalentAPIClient", return_value=mock_client
    )

    with pytest.raises(MissingLatticeRecordError):
        get_result(dispatch_id)


def test_get_status_only(mocker):
    """Check get_result when status_only=True"""

    dispatch_id = "test_get_result_st"
    mock_get_result_export = mocker.patch(
        "covalent._results_manager.results_manager._get_result_export_from_dispatcher",
        return_value={"id": dispatch_id, "status": "RUNNING"},
    )

    status_report = get_result(dispatch_id, status_only=True)
    assert status_report["status"] == "RUNNING"


def test_download_asset(mocker):
    dispatch_id = "test_download_asset"
    remote_uri = f"http://localhost:48008/api/v2/dispatches/{dispatch_id}/assets/result"
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client.get = MagicMock(return_value=mock_response)
    mocker.patch(
        "covalent._results_manager.results_manager.CovalentAPIClient", return_value=mock_client
    )

    def mock_generator():
        yield "Hello".encode("utf-8")

    mock_response.iter_content = MagicMock(return_value=mock_generator())

    with tempfile.NamedTemporaryFile() as local_file:
        download_asset(remote_uri, local_file.name)
        assert local_file.read().decode("utf-8") == "Hello"
