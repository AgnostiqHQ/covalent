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

"""Unit tests for transport graph operations module."""

import pytest

from covalent._workflow.transport import _TransportGraph
from covalent._workflow.transport_graph_ops import TransportGraphOps


def add(x, y):
    return x + y


def multiply(x, y):
    return x * y


def identity(x):
    return x


@pytest.fixture
def tg():
    """Transport graph operations fixture."""
    tg = _TransportGraph()
    tg.add_node(name="add", function=add, metadata={"0-mock-key": "0-mock-value"})
    tg.add_node(name="multiply", function=multiply, metadata={"1-mock-key": "1-mock-value"})
    tg.add_node(name="identity", function=identity, metadata={"2-mock-key": "2-mock-value"})
    return tg


@pytest.fixture
def tg_ops(tg):
    """Transport graph operations fixture."""
    return TransportGraphOps(tg)


def test_init(tg):
    """Test initialization of transport graph operations."""
    tg_ops = TransportGraphOps(tg)
    assert tg_ops.tg == tg
    assert tg_ops._status_map == {1: True, -1: False}


def test_flag_successors_no_successors(tg, tg_ops):
    """Test flagging successors of a node."""
    node_statuses = {0: 1, 1: 1, 2: 1}
    tg_ops._flag_successors(tg._graph, node_statuses=node_statuses, starting_node=0)
    assert node_statuses == {0: -1, 1: 1, 2: 1}


@pytest.mark.parametrize(
    "n_1,n_2,n_start,label,new_statuses",
    [
        (0, 1, 0, "01", {0: -1, 1: -1, 2: 1}),
        (1, 2, 0, "12", {0: -1, 1: 1, 2: 1}),
        (1, 2, 1, "12", {0: 1, 1: -1, 2: -1}),
        (1, 2, 2, "12", {0: 1, 1: 1, 2: -1}),
    ],
)
def test_flag_successors_with_one_successors(tg, tg_ops, n_1, n_2, n_start, label, new_statuses):
    """Test flagging successors of a node."""
    tg.add_edge(n_1, n_2, label)
    node_statuses = {0: 1, 1: 1, 2: 1}
    tg_ops._flag_successors(tg._graph, node_statuses=node_statuses, starting_node=n_start)
    assert node_statuses == new_statuses


@pytest.mark.parametrize(
    "n_1,n_2,n_3,n_4,label_1,label_2,n_start,new_statuses",
    [
        (0, 1, 1, 2, "01", "12", 0, {0: -1, 1: -1, 2: -1}),
        (0, 1, 0, 2, "01", "02", 0, {0: -1, 1: -1, 2: -1}),
        (0, 1, 0, 2, "01", "12", 1, {0: 1, 1: -1, 2: 1}),
    ],
)
def test_flag_successors_with_successors_3(
    tg, tg_ops, n_1, n_2, n_3, n_4, label_1, n_start, label_2, new_statuses
):
    """Test flagging successors of a node."""
    tg.add_edge(n_1, n_2, label_1)
    tg.add_edge(n_3, n_4, label_2)
    node_statuses = {0: 1, 1: 1, 2: 1}
    tg_ops._flag_successors(tg._graph, node_statuses=node_statuses, starting_node=n_start)
    assert node_statuses == new_statuses


def test_is_same_node_true(tg, tg_ops):
    """Test the is same node method."""
    assert tg_ops.is_same_node(tg._graph, 0) is True
    assert tg_ops.is_same_node(tg._graph, 1) is True


def test_is_same_node_false(tg_ops):
    """Test the is same node method."""
    tg = _TransportGraph()
    tg.add_node(name="multiply", function=add, metadata={"0- mock-key": "0-mock-value"})
    assert tg_ops.is_same_node(tg._graph, 0) is False


def test_is_same_edge_attributes_true(tg, tg_ops):
    """Test the is same edge attributes method."""
    tg.add_edge(0, 1, edge_name="01", kwargs={"x": 1, "y": 2})
    assert tg_ops.is_same_edge_attributes(tg._graph, 0, 1) is True


def test_is_same_edge_attributes_false(tg, tg_ops):
    """Test the is same edge attributes method."""
    tg.add_edge(0, 1, edge_name="01", kwargs={"x": 1, "y": 2})

    tg_2 = _TransportGraph()
    tg_2.add_node(name="add", function=add, metadata={"0- mock-key": "0-mock-value"})
    tg_2.add_node(name="multiply", function=multiply, metadata={"1- mock-key": "1-mock-value"})
    tg_2.add_node(name="identity", function=identity, metadata={"2- mock-key": "2-mock-value"})
    tg_2.add_edge(0, 1, edge_name="01", kwargs={"x": 1})

    assert tg_ops.is_same_edge_attributes(tg_2._graph, 0, 1) is False


def test_copy_nodes(tg, tg_ops):
    """Test the node copying method."""

    def replacement(x):
        return x + 1

    tg_new = _TransportGraph()
    tg_new.add_node(
        name="replacement", function=replacement, metadata={"0-mock-key": "0-mock-value"}
    )
    tg_new.add_node(name="multiply", function=multiply, metadata={"1-mock-key": "1-mock-value"})
    tg_new.add_node(
        name="replacement", function=replacement, metadata={"2-mock-key": "2-mock-value"}
    )

    tg_ops.copy_nodes_from(tg_new, [0, 2])
    tg_ops.tg._graph.nodes(data=True)[0]["name"] == tg_ops.tg._graph.nodes(data=True)[2][
        "name"
    ] == "replacement"
    tg_ops.tg._graph.nodes(data=True)[2]["name"] == "multiply"


def test_cmp_name_and_pval():
    pass


def test_get_diff_nodes():
    pass
