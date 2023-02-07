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

"""
Tests for the core functionality of the dispatcher.
"""


from typing import Dict, List

import pytest

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.dispatcher import (
    _get_abstract_task_inputs,
    _get_initial_tasks_and_deps,
    _handle_completed_node,
)
from covalent_dispatcher._dal.result import Result as SRVResult
from covalent_dispatcher._dal.result import get_result_object
from covalent_dispatcher._db import models, update
from covalent_dispatcher._db.datastore import DataStore


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def get_mock_result() -> Result:
    """Construct a mock result object corresponding to a lattice."""

    import sys

    @ct.electron(executor="local")
    def task(x):
        print(f"stdout: {x}")
        print("Error!", file=sys.stderr)
        return x

    @ct.lattice
    def pipeline(x):
        res1 = task(x)
        res2 = task(res1)
        return res2

    pipeline.build_graph(x="absolute")
    received_workflow = Lattice.deserialize_from_json(pipeline.serialize_to_json())
    result_object = Result(received_workflow, "pipeline_workflow")

    return result_object


def get_mock_srvresult(sdkres, test_db) -> SRVResult:

    sdkres._initialize_nodes()

    with test_db.session() as session:
        record = session.query(models.Lattice).where(models.Lattice.id == 1).first()

    update.persist(sdkres)

    return get_result_object(sdkres.dispatch_id)


@pytest.mark.asyncio
async def test_get_abstract_task_inputs(mocker, test_db):
    """Test _get_abstract_task_inputs for both dicts and list parameter types"""

    @ct.electron
    def list_task(arg: List):
        return len(arg)

    @ct.electron
    def dict_task(arg: Dict):
        return len(arg)

    @ct.electron
    def multivariable_task(x, y):
        return x, y

    @ct.lattice
    def list_workflow(arg):
        return list_task(arg)

    @ct.lattice
    def dict_workflow(arg):
        return dict_task(arg)

    #    1   2
    #     \   \
    #      0   3
    #     / /\/
    #     4   5

    @ct.electron
    def identity(x):
        return x

    @ct.lattice
    def multivar_workflow(x, y):
        electron_x = identity(x)
        electron_y = identity(y)
        res1 = multivariable_task(electron_x, electron_y)
        res2 = multivariable_task(electron_y, electron_x)
        res3 = multivariable_task(electron_y, electron_x)
        res4 = multivariable_task(electron_x, electron_y)
        return 1

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    # list-type inputs

    # Nodes 0=task, 1=:electron_list:, 2=1, 3=2, 4=3
    list_workflow.build_graph([1, 2, 3])
    abstract_args = [2, 3, 4]
    tg = list_workflow.transport_graph

    sdkres = Result(lattice=list_workflow, dispatch_id="list_input_dispatch")
    result_object = get_mock_srvresult(sdkres, test_db)
    dispatch_id = result_object.dispatch_id

    async def mock_get_incoming_edges(dispatch_id, node_id):
        return result_object.lattice.transport_graph.get_incoming_edges(node_id)

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_incoming_edges",
        mock_get_incoming_edges,
    )

    abs_task_inputs = await _get_abstract_task_inputs(
        result_object.dispatch_id, 1, tg.get_node_value(1, "name")
    )

    expected_inputs = {"args": abstract_args, "kwargs": {}}

    assert abs_task_inputs == expected_inputs

    # dict-type inputs

    # Nodes 0=task, 1=:electron_dict:, 2=1, 3=2
    dict_workflow.build_graph({"a": 1, "b": 2})
    abstract_args = {"a": 2, "b": 3}
    tg = dict_workflow.transport_graph

    sdkres = Result(lattice=dict_workflow, dispatch_id="dict_input_dispatch")
    result_object = get_mock_srvresult(sdkres, test_db)

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_incoming_edges",
        mock_get_incoming_edges,
    )

    task_inputs = await _get_abstract_task_inputs(
        result_object.dispatch_id, 1, tg.get_node_value(1, "name")
    )
    expected_inputs = {"args": [], "kwargs": abstract_args}

    assert task_inputs == expected_inputs

    # Check arg order
    multivar_workflow.build_graph(1, 2)
    received_lattice = Lattice.deserialize_from_json(multivar_workflow.serialize_to_json())
    sdkres = Result(lattice=received_lattice, dispatch_id="arg_order_dispatch")
    result_object = get_mock_srvresult(sdkres, test_db)
    tg = received_lattice.transport_graph

    # Account for injected postprocess electron
    assert list(tg._graph.nodes) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    tg.set_node_value(0, "output", ct.TransportableObject(1))
    tg.set_node_value(2, "output", ct.TransportableObject(2))

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_incoming_edges",
        mock_get_incoming_edges,
    )

    task_inputs = await _get_abstract_task_inputs(
        result_object.dispatch_id, 4, tg.get_node_value(4, "name")
    )
    assert task_inputs["args"] == [0, 2]

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_incoming_edges",
        mock_get_incoming_edges,
    )

    task_inputs = await _get_abstract_task_inputs(
        result_object.dispatch_id, 5, tg.get_node_value(5, "name")
    )
    assert task_inputs["args"] == [2, 0]

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_incoming_edges",
        mock_get_incoming_edges,
    )

    task_inputs = await _get_abstract_task_inputs(
        result_object.dispatch_id, 6, tg.get_node_value(6, "name")
    )
    assert task_inputs["args"] == [2, 0]
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_incoming_edges",
        mock_get_incoming_edges,
    )

    task_inputs = await _get_abstract_task_inputs(
        result_object.dispatch_id, 7, tg.get_node_value(7, "name")
    )
    assert task_inputs["args"] == [0, 2]


@pytest.mark.asyncio
async def test_handle_completed_node(mocker, test_db):
    """Unit test for completed node handler"""

    from covalent_dispatcher._core.dispatcher import _initialize_caches, _pending_parents

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    pending_parents = {}
    sorted_task_groups = {}
    sdkres = get_mock_result()
    result_object = get_mock_srvresult(sdkres, test_db)

    async def get_node_successors(dispatch_id: str, node_id: int):
        return result_object.lattice.transport_graph.get_successors(node_id, ["task_group_id"])

    async def get_electron_attribute(dispatch_id, node_id, key):
        return node_id

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_node_successors",
        get_node_successors,
    )

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_electron_attribute",
        get_electron_attribute,
    )

    # tg edges are (1, 0), (0, 2)
    pending_parents[0] = 1
    pending_parents[1] = 0
    pending_parents[2] = 1
    sorted_task_groups[0] = [0]
    sorted_task_groups[1] = [1]
    sorted_task_groups[2] = [2]

    await _initialize_caches(result_object.dispatch_id, pending_parents, sorted_task_groups)

    node_result = {"node_id": 1, "status": Result.COMPLETED}
    assert await _pending_parents.get_pending(result_object.dispatch_id, 0) == 1
    assert await _pending_parents.get_pending(result_object.dispatch_id, 1) == 0
    assert await _pending_parents.get_pending(result_object.dispatch_id, 2) == 1

    next_nodes = await _handle_completed_node(result_object.dispatch_id, 1)
    assert next_nodes == [0]

    assert await _pending_parents.get_pending(result_object.dispatch_id, 0) == 0
    assert await _pending_parents.get_pending(result_object.dispatch_id, 1) == 0
    assert await _pending_parents.get_pending(result_object.dispatch_id, 2) == 1


@pytest.mark.asyncio
async def test_get_initial_tasks_and_deps(mocker, test_db):
    """Test internal function for initializing status_queue and pending_parents"""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    pending_parents = {}

    sdkres = get_mock_result()
    result_object = get_mock_srvresult(sdkres, test_db)
    dispatch_id = result_object.dispatch_id

    async def get_graph_nodes_links(dispatch_id: str) -> dict:
        import networkx as nx

        """Return the internal transport graph in NX node-link form"""
        g = result_object.lattice.transport_graph.get_internal_graph_copy()
        return nx.readwrite.node_link_data(g)

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_graph_nodes_links",
        side_effect=get_graph_nodes_links,
    )

    initial_nodes, pending_parents, sorted_task_groups = await _get_initial_tasks_and_deps(
        dispatch_id
    )

    assert initial_nodes == [1]

    # Account for injected postprocess electron
    assert pending_parents == {0: 1, 1: 0, 2: 1, 3: 3}
    assert sorted_task_groups == {0: [0], 1: [1], 2: [2], 3: [3]}
