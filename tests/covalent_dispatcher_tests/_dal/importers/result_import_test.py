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

"""Tests for importing ResultSchema into the DB"""

import copy
import tempfile

import pytest

import covalent as ct
from covalent._results_manager.result import Result as SDKResult
from covalent._serialize.result import serialize_result
from covalent._shared_files.schemas.result import AssetSchema, ResultSchema
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent_dispatcher._dal.importers.result import SERVER_URL, handle_redispatch, import_result
from covalent_dispatcher._dal.result import get_result_object
from covalent_dispatcher._db.datastore import DataStore

TEMP_RESULTS_DIR = "/tmp/covalent_result_import_test"


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def get_mock_result(dispatch_id, tmpdir) -> ResultSchema:
    """Construct a mock result object corresponding to a lattice."""

    @ct.electron(executor="local")
    def task(x):
        return x

    @ct.lattice(deps_bash=ct.DepsBash(["ls"]))
    def workflow(x):
        res1 = task(x)
        return res1

    workflow.build_graph(x=1)

    sdk_res = SDKResult(workflow, dispatch_id=dispatch_id)

    return serialize_result(sdk_res, tmpdir)


def test_import_result(mocker, test_db):
    dispatch_id = "test_import_result"

    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    with tempfile.TemporaryDirectory(prefix="covalent-") as sdk_dir, tempfile.TemporaryDirectory(
        prefix="covalent-"
    ) as srv_dir:
        res = get_mock_result(dispatch_id, sdk_dir)
        filtered_res = import_result(res, srv_dir, None)

    assert res.metadata == filtered_res.metadata

    # Check assets

    assets = res.assets
    filtered_assets = filtered_res.assets

    assert assets.result.digest == filtered_assets.result.digest
    assert assets.result.uri == filtered_assets.result.uri
    assert filtered_assets.result.remote_uri.startswith(SERVER_URL)

    assert assets.error.digest == filtered_assets.error.digest
    assert assets.error.uri == filtered_assets.error.uri
    assert filtered_assets.error.remote_uri.startswith(SERVER_URL)

    lat = res.lattice
    filtered_lat = filtered_res.lattice

    assert lat.metadata == filtered_lat.metadata

    assets = lat.assets
    filtered_assets = filtered_lat.assets

    assert assets.workflow_function.digest == filtered_assets.workflow_function.digest
    assert assets.workflow_function.uri == filtered_assets.workflow_function.uri
    assert filtered_assets.workflow_function.remote_uri.startswith(SERVER_URL)

    assert assets.doc.digest == filtered_assets.doc.digest
    assert assets.doc.uri == filtered_assets.doc.uri
    assert filtered_assets.doc.remote_uri.startswith(SERVER_URL)

    assert assets.inputs.digest == filtered_assets.inputs.digest
    assert assets.inputs.uri == filtered_assets.inputs.uri
    assert filtered_assets.inputs.remote_uri.startswith(SERVER_URL)

    tg = lat.transport_graph
    filtered_tg = filtered_lat.transport_graph

    for i, node in enumerate(tg.nodes):
        filtered_node = filtered_tg.nodes[i]
        assert node.metadata == filtered_node.metadata
        filtered_node.assets.function.remote_uri.startswith(SERVER_URL)

    for i, edge in enumerate(tg.links):
        assert edge == filtered_tg.links[i]


def test_import_previously_imported_result(mocker, test_db):
    dispatch_id = "test_import_previous_result"
    sub_dispatch_id = "test_import_previous_result_sub"

    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    mock_filter_uris = mocker.patch(
        "covalent_dispatcher._dal.importers.result._filter_remote_uris"
    )

    with tempfile.TemporaryDirectory(prefix="covalent-") as sdk_dir, tempfile.TemporaryDirectory(
        prefix="covalent-"
    ) as srv_dir:
        res = get_mock_result(dispatch_id, sdk_dir)
        import_result(res, srv_dir, None)

    with tempfile.TemporaryDirectory(prefix="covalent-") as sdk_dir, tempfile.TemporaryDirectory(
        prefix="covalent-"
    ) as srv_dir:
        sub_res = get_mock_result(sub_dispatch_id, sdk_dir)
        import_result(sub_res, srv_dir, None)
        srv_res = get_result_object(dispatch_id, bare=True)
        parent_node = srv_res.lattice.transport_graph.get_node(0)

    with tempfile.TemporaryDirectory(prefix="covalent-") as srv_dir:
        import_result(sub_res, srv_dir, parent_node._electron_id)

    sub_srv_res = get_result_object(sub_dispatch_id, bare=True)
    assert mock_filter_uris.call_count == 2
    assert sub_srv_res._electron_id == parent_node._electron_id


@pytest.mark.parametrize(
    "parent_status,new_status",
    [
        (RESULT_STATUS.COMPLETED, RESULT_STATUS.PENDING_REUSE),
        (RESULT_STATUS.CANCELLED, RESULT_STATUS.NEW_OBJECT),
        (RESULT_STATUS.NEW_OBJECT, RESULT_STATUS.NEW_OBJECT),
    ],
)
def test_handle_redispatch_identical(mocker, test_db, parent_status, new_status):
    """Test redispatching a workflow with no modifications."""

    dispatch_id = "test_handle_redispatch"
    redispatch_id = "test_handle_redispatch_2"

    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mock_copy_node_asset = mocker.patch("covalent_dispatcher._dal.tg_ops.copy_asset")
    mock_copy_asset_meta = mocker.patch("covalent_dispatcher._dal.asset.copy_asset_meta")
    mock_copy_workflow_asset_meta = mocker.patch(
        "covalent_dispatcher._dal.importers.result.copy_asset_meta"
    )

    with tempfile.TemporaryDirectory(prefix="covalent-") as sdk_dir, tempfile.TemporaryDirectory(
        prefix="covalent-"
    ) as srv_dir:
        manifest = get_mock_result(dispatch_id, sdk_dir)

        redispatch_manifest = copy.deepcopy(manifest)
        redispatch_manifest.metadata.dispatch_id = redispatch_id
        redispatch_manifest.metadata.root_dispatch_id = redispatch_id

        import_result(manifest, srv_dir, None)

        parent_result_object = get_result_object(dispatch_id, bare=False)
        tg = parent_result_object.lattice.transport_graph
        for n in tg._graph.nodes:
            tg.set_node_value(n, "status", parent_status)

    with tempfile.TemporaryDirectory(prefix="covalent-") as srv_dir_2:
        # Import the redispatch manifest and filter it through handle_redispatch
        redispatch_manifest = import_result(redispatch_manifest, srv_dir_2, None)
        redispatch_manifest, assets_to_copy = handle_redispatch(
            redispatch_manifest, dispatch_id, True
        )

    n_workflow_assets = 0
    for key, asset in redispatch_manifest.assets:
        n_workflow_assets += 1
        assert asset.remote_uri == ""

    for key, asset in redispatch_manifest.lattice.assets:
        n_workflow_assets += 1
        assert asset.remote_uri == ""

    n_electron_assets = 0
    for node in redispatch_manifest.lattice.transport_graph.nodes:
        for key, asset in node.assets:
            n_electron_assets += 1
            assert asset.remote_uri == ""

    assert mock_copy_workflow_asset_meta.call_count == n_workflow_assets + n_electron_assets

    result_object = get_result_object(redispatch_id, bare=False)
    tg = result_object.lattice.transport_graph
    for n in tg._graph.nodes:
        assert tg.get_node_value(n, "status") == new_status

    assert len(assets_to_copy) == n_workflow_assets + n_electron_assets


def test_import_result_with_custom_assets(mocker, test_db):
    dispatch_id = "test_import_result"

    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    with tempfile.TemporaryDirectory(prefix="covalent-") as sdk_dir, tempfile.TemporaryDirectory(
        prefix="covalent-"
    ) as srv_dir:
        manifest = get_mock_result(dispatch_id, sdk_dir)
        manifest.lattice.custom_assets = {"custom_lattice_asset": AssetSchema()}
        manifest.lattice.transport_graph.nodes[0].custom_assets = {
            "custom_electron_asset": AssetSchema()
        }
        filtered_res = import_result(manifest, srv_dir, None)

    with test_db.session() as session:
        result_object = get_result_object(dispatch_id, bare=True, session=session)
        node_0 = result_object.lattice.transport_graph.get_node(0, session)
        node_1 = result_object.lattice.transport_graph.get_node(1, session)
        lat_asset_ids = result_object.lattice.get_asset_ids(session, [])
        node_0_asset_ids = node_0.get_asset_ids(session, [])
        node_1_asset_ids = node_1.get_asset_ids(session, [])
    assert "custom_lattice_asset" in lat_asset_ids
    assert "custom_electron_asset" in node_0_asset_ids
    assert "custom_electron_asset" not in node_1_asset_ids
