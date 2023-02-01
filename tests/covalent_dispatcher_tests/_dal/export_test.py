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
from covalent._workflow.lattice import Lattice as SDKLattice
from covalent_dispatcher._dal.export import (
    _to_client_graph,
    _to_client_lattice,
    export_serialized_result,
)
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
    mocker.patch("covalent_dispatcher._db.utils.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

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
    assert "output" not in sdk_graph._graph.nodes[1]
    assert "value" not in sdk_graph._graph.nodes[0]
    assert "value" in sdk_graph._graph.nodes[1]


def test_to_client_lattice(test_db, mocker):
    from datetime import datetime

    import covalent as ct

    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.utils.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

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
    assert sdk_lattice.metadata == res.lattice.metadata
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
    mocker.patch("covalent_dispatcher._db.utils.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    update.persist(res)

    srv_res = get_result_object(res.dispatch_id)

    ts = datetime.now()
    srv_res._start_time = ts
    srv_res._status = SDKResult.RUNNING
    srv_res.commit()

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
    assert sdk_lat.metadata == res.lattice.metadata
    assert sdk_lat.named_args == res.lattice.named_args
    assert sdk_lat.named_kwargs == res.lattice.named_kwargs
    assert sdk_lat.lattice_imports == res.lattice.lattice_imports
    assert sdk_lat.cova_imports == res.lattice.cova_imports

    assert ser_res["start_time"] == ts.isoformat()
    assert ser_res["end_time"] is None
    assert ser_res["status"] == str(SDKResult.RUNNING)

    srv_res._end_time = ts
    srv_res._status = SDKResult.COMPLETED
    srv_res.commit()
    res_export = export_serialized_result(res.dispatch_id)

    ser_res = res_export["result"]
    assert ser_res["end_time"] == ts.isoformat()
    assert ser_res["status"] == str(SDKResult.COMPLETED)
