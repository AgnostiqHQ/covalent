# Copyright 2021 Agnostiq Inc.
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

"""Tests for DB-backed electron"""

from datetime import datetime

import pytest

import covalent as ct
from covalent._results_manager import Result as SDKResult
from covalent._workflow.lattice import Lattice as SDKLattice
from covalent.executor import LocalExecutor
from covalent_dispatcher._dal.tg import _TransportGraph
from covalent_dispatcher._db import models, update
from covalent_dispatcher._db.datastore import DataStore


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


le = LocalExecutor(log_stdout="/tmp/stdout.log")


def get_mock_result() -> SDKResult:
    """Construct a mock result object corresponding to a lattice."""

    @ct.electron(executor=le)
    def task(x, y):
        return x + y

    @ct.lattice(deps_bash=ct.DepsBash(["ls"]))
    def workflow(x, y=0):
        res1 = task(x, y=y)
        return res1

    workflow.build_graph(x=1)
    received_workflow = SDKLattice.deserialize_from_json(workflow.serialize_to_json())
    result_object = SDKResult(received_workflow, "mock_dispatch")

    return result_object


def test_transport_graph_attributes(test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )
        lat_id = record.id

    tg = _TransportGraph.get_compute_graph(session, lat_id, bare=False)
    assert list(tg._graph.nodes) == [0, 1, 2, 3]
    assert tg._graph.nodes[0]["task_group_id"] == 0
    assert tg.get_dependencies(0) == [1, 2]
    e_data = tg.get_edge_data(1, 0)
    assert e_data[0]["edge_name"] == "x"
    assert e_data[0]["param_type"] == "arg"
    assert e_data[0]["arg_index"] == 0

    e_data = tg.get_edge_data(2, 0)
    assert e_data[0]["edge_name"] == "y"
    assert e_data[0]["param_type"] == "kwarg"


@pytest.mark.parametrize("bare_mode", [False, True])
def test_transport_graph_get_set(bare_mode, test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )
        lat_id = record.id

    tg = _TransportGraph.get_compute_graph(session, lat_id, bare_mode)

    assert tg.get_node_value(0, "name") == "task"
    assert tg.get_node_value(0, "executor") == "local"
    assert tg.get_node_value(0, "executor_data") == le.to_dict()

    assert tg.get_values_for_nodes([0], ["name", "executor"])[0] == {
        "name": "task",
        "executor": "local",
    }

    tg.set_node_value(1, "status", SDKResult.COMPLETED)
    assert tg.get_node_value(1, "status") == SDKResult.COMPLETED

    ts = datetime.now()
    tg.set_node_value(0, "end_time", ts)
    tg.set_node_value(0, "status", SDKResult.COMPLETED)
    assert tg.get_node_value(0, "status") == SDKResult.COMPLETED
    assert tg.get_node_value(0, "end_time") == ts

    # Check handling of invalid node id
    with pytest.raises(KeyError):
        tg.get_node_value(-5, "name")


def test_transport_graph_get_internal_graph_copy(test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )
        lat_id = record.id

    tg = _TransportGraph.get_compute_graph(session, lat_id)

    g = tg.get_internal_graph_copy()

    assert g.nodes == tg._graph.nodes
    assert g.edges == tg._graph.edges


@pytest.mark.parametrize("bare_mode", [False, True])
def test_transport_graph_get_incoming_edges(bare_mode, test_db, mocker):
    @ct.electron(executor="local")
    def task(x, y, z):
        return x + y + z

    @ct.electron(executor="local")
    def prod(x, y, z):
        return x * y * z

    @ct.lattice(deps_bash=ct.DepsBash(["ls"]))
    def workflow(x, y=1):
        res1 = task(x, x, y)
        res2 = prod(res1, res1, x)
        return res1

    workflow.build_graph(x=1)

    received_workflow = SDKLattice.deserialize_from_json(workflow.serialize_to_json())
    res = SDKResult(received_workflow, "mock_dispatch")

    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )
        lat_id = record.id

    tg = _TransportGraph.get_compute_graph(session, lat_id, bare=bare_mode)
    in_edges = tg.get_incoming_edges(0)

    assert len(in_edges) == 3

    e_by_parent = sorted(in_edges, key=lambda e: e["source"])
    assert e_by_parent[0]["attrs"]["edge_name"] == "x"
    assert e_by_parent[0]["attrs"]["param_type"] == "arg"
    assert e_by_parent[0]["attrs"]["arg_index"] == 0

    assert e_by_parent[1]["attrs"]["edge_name"] == "y"
    assert e_by_parent[1]["attrs"]["param_type"] == "arg"
    assert e_by_parent[1]["attrs"]["arg_index"] == 1

    assert e_by_parent[2]["attrs"]["edge_name"] == "z"
    assert e_by_parent[2]["attrs"]["param_type"] == "arg"
    assert e_by_parent[2]["attrs"]["arg_index"] == 2

    in_edges = tg.get_incoming_edges(4)
    assert len(in_edges) == 3

    e_by_parent = sorted(in_edges, key=lambda e: e["source"])

    assert e_by_parent[0]["source"] == 0
    assert e_by_parent[0]["attrs"]["edge_name"] == "x"
    assert e_by_parent[0]["attrs"]["param_type"] == "arg"
    assert e_by_parent[0]["attrs"]["arg_index"] == 0

    assert e_by_parent[1]["source"] == 0
    assert e_by_parent[1]["attrs"]["edge_name"] == "y"
    assert e_by_parent[1]["attrs"]["param_type"] == "arg"
    assert e_by_parent[1]["attrs"]["arg_index"] == 1

    assert e_by_parent[2]["source"] == 5
    assert e_by_parent[2]["attrs"]["edge_name"] == "z"
    assert e_by_parent[2]["attrs"]["param_type"] == "arg"
    assert e_by_parent[2]["attrs"]["arg_index"] == 2


@pytest.mark.parametrize("bare_mode", [False, True])
def test_transport_graph_get_edge_data(bare_mode, test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )
        lat_id = record.id

    ref_tg = _TransportGraph.get_compute_graph(session, lat_id, bare=False)
    tg = _TransportGraph.get_compute_graph(session, lat_id, bare=bare_mode)

    child = tg.get_node(0)

    ref_e_data = ref_tg._graph.get_edge_data(1, 0)
    e_data = tg.get_edge_data(1, 0)
    assert len(ref_e_data) == 1
    assert len(e_data) == 1
    assert ref_e_data == e_data

    ref_e_data = tg.get_edge_data(2, 0)
    e_data = tg.get_edge_data(2, 0)
    assert len(ref_e_data) == 1
    assert len(e_data) == 1
    assert ref_e_data == e_data


@pytest.mark.parametrize("bare_mode", [False, True])
def test_transport_graph_get_successors(bare_mode, test_db, mocker):
    @ct.electron(executor="local")
    def task(x, y, z):
        return x + y + z

    @ct.electron(executor="local")
    def prod(x, y, z):
        return x * y * z

    @ct.lattice(deps_bash=ct.DepsBash(["ls"]))
    def workflow(x, y=1):
        res1 = task(x, x, y)
        res2 = prod(res1, res1, x)
        res3 = prod(res1, res1, res1)
        return res1

    workflow.build_graph(x=1)

    received_workflow = SDKLattice.deserialize_from_json(workflow.serialize_to_json())
    res = SDKResult(received_workflow, "mock_dispatch")

    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )
        lat_id = record.id

    tg = _TransportGraph.get_compute_graph(session, lat_id, bare=bare_mode)

    node_list = tg.get_successors(0, attr_keys=["status"])
    assert [n["node_id"] for n in node_list] == [4, 4, 6, 6, 6, 7, 7]
    assert node_list[0]["status"] == SDKResult.NEW_OBJ
