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

"""Tests for DB-backed Result"""


from datetime import datetime

import pytest

import covalent as ct
from covalent._results_manager import Result as SDKResult
from covalent._serialize.result import serialize_result
from covalent._workflow.lattice import Lattice as SDKLattice
from covalent_dispatcher._dal.export import (
    _to_client_graph,
    _to_client_lattice,
    export_result_manifest,
    export_serialized_result,
)
from covalent_dispatcher._dal.importers.result import import_result
from covalent_dispatcher._dal.result import get_result_object
from covalent_dispatcher._db import update
from covalent_dispatcher._db.datastore import DataStore


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def get_mock_result() -> SDKResult:
    """Construct a mock result object corresponding to a lattice."""

    @ct.electron(executor="local")
    def task(x):
        return x

    @ct.lattice(deps_bash=ct.DepsBash(["ls"]))
    def workflow(x):
        res1 = task(x)
        return res1

    workflow.build_graph(x=1)
    received_workflow = SDKLattice.deserialize_from_json(workflow.serialize_to_json())
    result_object = SDKResult(received_workflow, "mock_dispatch")

    return result_object


def test_to_client_graph(test_db, mocker):
    from datetime import datetime

    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    result = get_result_object(res.dispatch_id)

    srv_graph = result.lattice.transport_graph
    ts = datetime.now()
    srv_graph.set_node_value(1, "start_time", ts)
    srv_graph.set_node_value(1, "end_time", ts)
    srv_graph.set_node_value(1, "status", SDKResult.COMPLETED)
    srv_graph.set_node_value(1, "output", ct.TransportableObject(1))
    sdk_graph = _to_client_graph(srv_graph)
    assert list(srv_graph._graph.nodes) == list(sdk_graph._graph.nodes)

    assert sdk_graph.get_node_value(0, "name") == srv_graph.get_node_value(0, "name")

    for key in ["name", "start_time", "end_time", "status", "value"]:
        assert sdk_graph.get_node_value(1, key) == srv_graph.get_node_value(1, key)

    metadata = sdk_graph.get_node_value(0, "metadata")

    assert metadata == res.lattice.transport_graph.get_node_value(0, "metadata")
    assert sdk_graph.get_node_value(0, "sub_dispatch_id") is None

    assert "output" not in sdk_graph._graph.nodes[0]
    assert "output" in sdk_graph._graph.nodes[1]
    assert "value" not in sdk_graph._graph.nodes[0]
    assert "value" in sdk_graph._graph.nodes[1]


def test_to_client_lattice(test_db, mocker):
    from datetime import datetime

    import covalent as ct

    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    result = get_result_object(res.dispatch_id)

    srv_lattice = result.lattice
    sdk_lattice = _to_client_lattice(srv_lattice)

    print(sdk_lattice)
    print(sdk_lattice.__dict__)

    assert sdk_lattice.__dict__.keys() == res.lattice.__dict__.keys()
    assert (
        sdk_lattice.workflow_function.get_serialized()
        == res.lattice.workflow_function.get_serialized()
    )
    assert sdk_lattice.workflow_function_string == res.lattice.workflow_function_string

    # Triggers aren't saved server-side
    del res.lattice.metadata["triggers"]

    assert sdk_lattice.metadata == res.lattice.metadata
    assert sdk_lattice.inputs == res.lattice.inputs
    assert sdk_lattice.named_args == res.lattice.named_args
    assert sdk_lattice.named_kwargs == res.lattice.named_kwargs
    assert sdk_lattice.lattice_imports == res.lattice.lattice_imports
    assert sdk_lattice.cova_imports == res.lattice.cova_imports

    sdk_lattice = SDKLattice.deserialize_from_json(sdk_lattice.serialize_to_json())

    assert sdk_lattice.__dict__.keys() == res.lattice.__dict__.keys()
    assert (
        sdk_lattice.workflow_function.get_serialized()
        == res.lattice.workflow_function.get_serialized()
    )
    assert sdk_lattice.workflow_function_string == res.lattice.workflow_function_string
    assert sdk_lattice.metadata == res.lattice.metadata
    assert sdk_lattice.named_args == res.lattice.named_args
    assert sdk_lattice.named_kwargs == res.lattice.named_kwargs
    assert sdk_lattice.lattice_imports == res.lattice.lattice_imports
    assert sdk_lattice.cova_imports == res.lattice.cova_imports


def test_to_client_result(test_db, mocker):
    from datetime import datetime

    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    srv_res = get_result_object(res.dispatch_id)

    ts = datetime.now()
    srv_res._update_dispatch(start_time=ts, status=SDKResult.RUNNING)

    res_export = export_serialized_result(res.dispatch_id)

    ser_res = res_export["result"]
    ser_lat = res_export["lattice"]

    sdk_lat = SDKLattice.deserialize_from_json(ser_lat)
    assert sdk_lat.__dict__.keys() == res.lattice.__dict__.keys()
    assert (
        sdk_lat.workflow_function.get_serialized()
        == res.lattice.workflow_function.get_serialized()
    )
    assert sdk_lat.workflow_function_string == res.lattice.workflow_function_string

    # Triggers are not saved in the db
    del res.lattice.metadata["triggers"]

    assert sdk_lat.metadata == res.lattice.metadata
    assert sdk_lat.inputs == res.lattice.inputs
    assert sdk_lat.named_args == res.lattice.named_args
    assert sdk_lat.named_kwargs == res.lattice.named_kwargs
    assert sdk_lat.lattice_imports == res.lattice.lattice_imports
    assert sdk_lat.cova_imports == res.lattice.cova_imports

    assert ser_res["start_time"] == ts.isoformat()
    assert ser_res["end_time"] is None
    assert ser_res["status"] == str(SDKResult.RUNNING)

    srv_res._update_dispatch(end_time=ts, status=SDKResult.COMPLETED)
    res_export = export_serialized_result(res.dispatch_id)

    ser_res = res_export["result"]
    assert ser_res["end_time"] == ts.isoformat()
    assert ser_res["status"] == str(SDKResult.COMPLETED)


def test_export_result_manifest(test_db, mocker):
    import tempfile
    from datetime import datetime

    res = get_mock_result()
    dispatch_id = "test_export_result_manifest"
    res._dispatch_id = dispatch_id
    res._root_dispatch_id = dispatch_id
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    with tempfile.TemporaryDirectory() as sdk_tmp_dir, tempfile.TemporaryDirectory() as srv_tmp_dir:
        manifest = serialize_result(res, sdk_tmp_dir)
        received_manifest = manifest.copy(deep=True)

        import_result(received_manifest, srv_tmp_dir, None)
        srv_res = get_result_object(dispatch_id)
        ts = datetime.now()
        srv_res._update_dispatch(start_time=ts, status=SDKResult.RUNNING)

        export_manifest = export_result_manifest(dispatch_id)

        assert export_manifest.metadata.start_time == ts
        assert export_manifest.metadata.status == str(SDKResult.RUNNING)


def test_import_export_manifest(test_db, mocker):
    """Check that Export(Import) == identity modulo asset uris"""

    import tempfile
    from datetime import datetime

    res = get_mock_result()
    dispatch_id = "test_import_export_manifest"
    res._dispatch_id = dispatch_id
    res._root_dispatch_id = dispatch_id
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    with tempfile.TemporaryDirectory() as sdk_tmp_dir, tempfile.TemporaryDirectory() as srv_tmp_dir:
        manifest = serialize_result(res, sdk_tmp_dir)
        received_manifest = manifest.copy(deep=True)

        import_result(received_manifest, srv_tmp_dir, None)

        export_manifest = export_result_manifest(dispatch_id)

        submitted = manifest.dict()
        exported = export_manifest.dict()

        # Check that workflow metadata are preserved
        for key in submitted["metadata"]:
            assert submitted["metadata"][key] == exported["metadata"][key]

        sub_lattice = submitted["lattice"]
        exp_lattice = exported["lattice"]
        for key in sub_lattice["metadata"]:
            assert sub_lattice["metadata"][key] == exp_lattice["metadata"][key]

        # Check workflow assets; uris are filtered by the server
        for key in submitted["assets"]:
            submitted["assets"][key].pop("uri")
            submitted["assets"][key].pop("remote_uri")
            exported["assets"][key].pop("uri")
            exported["assets"][key].pop("remote_uri")
            assert submitted["assets"][key] == exported["assets"][key]

        for key in sub_lattice["assets"]:
            sub_lattice["assets"][key].pop("uri")
            sub_lattice["assets"][key].pop("remote_uri")
            exp_lattice["assets"][key].pop("uri")
            exp_lattice["assets"][key].pop("remote_uri")
            assert sub_lattice["assets"][key] == exp_lattice["assets"][key]

        sub_tg = sub_lattice["transport_graph"]
        exp_tg = exp_lattice["transport_graph"]
        sorted(sub_tg["nodes"], key=lambda x: x["id"])
        sorted(exp_tg["nodes"], key=lambda x: x["id"])

        # Check transport graphs
        for i, sub_node in enumerate(sub_tg["nodes"]):
            exp_node = exp_tg["nodes"][i]
            for key in sub_node["assets"]:
                sub_node["assets"][key].pop("uri")
                sub_node["assets"][key].pop("remote_uri")
                exp_node["assets"][key].pop("uri")
                exp_node["assets"][key].pop("remote_uri")

                assert sub_node["assets"][key] == exp_node["assets"][key]

        assert sub_tg["links"] == exp_tg["links"]
