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

"""Unit tests for transport graph."""

import platform

import cloudpickle
import networkx as nx
import pytest

from covalent._shared_files.defaults import parameter_prefix
from covalent._workflow.transport import TransportableObject, _TransportGraph


def subtask(x):
    """Workflow subtask."""

    return x**2


def subtask_2(x):
    """Workflow subtask."""

    return x


@pytest.fixture
def transportable_object():
    """Transportable object fixture."""

    return TransportableObject(obj=subtask)


@pytest.fixture
def transport_graph():
    """Empty transport graph."""

    return _TransportGraph()


@pytest.fixture
def workflow_transport_graph():
    """
    Workflow transport graph with nodes.

    Note that edges have not been added.
    """

    tg = _TransportGraph()
    tg.add_node(
        name="square", kwargs={"x": 2}, function=subtask, metadata={"mock_field": "mock_value"}
    )
    tg.add_node(
        name="identity", kwargs={"x": 2}, function=subtask_2, metadata={"mock_field": "mock_value"}
    )
    return tg


def test_transportable_object_python_version(transportable_object):
    """Test that the transportable object retrieves the correct python version."""

    to = transportable_object
    assert to.python_version == platform.python_version()


def test_transportable_object_get_serialized(transportable_object):
    """Test serialized transportable object retrieval."""

    to = transportable_object
    assert to.get_serialized() == to._object


def test_transportable_object_get_deserialized(transportable_object):
    """Test deserialization of the transportable object."""

    to = transportable_object
    assert to.get_deserialized()(x=2) == subtask(x=2)


def test_transportable_object_serialize_deserialize(transportable_object):
    """Test that the transportable object is unchanged after serialization and deserialization."""

    to = transportable_object
    data = to.serialize()  # Serialize transportable object
    new_to = to.deserialize(data)  # Deserialize transportable object

    assert new_to.get_deserialized()(x=3) == subtask(x=3)
    assert new_to.python_version == to.python_version


def test_transport_graph_initialization():
    """Test the initialization of an empty transport graph."""

    tg = _TransportGraph()
    assert isinstance(tg._graph, nx.DiGraph)
    assert not tg.lattice_metadata


def test_transport_graph_add_nodes(transport_graph):
    """Test addition of nodes (electrons) to the transport graph."""

    tg = transport_graph
    assert len(tg._graph.nodes) == 0
    node_id = tg.add_node(
        name="square", kwargs={"x": 2}, function=subtask, metadata={"mock_field": "mock_value"}
    )
    assert len(tg._graph.nodes) == 1
    assert node_id == 0


def test_transport_graph_get_and_set_edges(workflow_transport_graph):
    """Test the setting and retrieval of edges to the transport graph."""

    wtg = workflow_transport_graph
    wtg.add_edge(x=0, y=1, edge_name="apples")
    assert wtg._graph.get_edge_data(0, 1) == {"edge_name": "apples"}
    assert wtg.get_edge_value(dep_key=0, node_key=1, value_key="edge_name") == "apples"


def test_transport_graph_transport_graph_reset(workflow_transport_graph):
    """Test that the transport graph reset method resets the graph."""

    wtg = workflow_transport_graph
    wtg.add_edge(x=0, y=1, edge_name="apples")
    assert list(wtg._graph.nodes) == [0, 1]
    assert list(wtg._graph.edges) == [(0, 1)]
    wtg.reset()
    assert list(wtg._graph.nodes) == []
    assert list(wtg._graph.edges) == []


def test_transport_graph_get_topologically_sorted_graph(workflow_transport_graph):
    """Test the topological graph sort method in the transport graph."""

    wtg = workflow_transport_graph
    assert wtg.get_topologically_sorted_graph() == [[0, 1]]


def test_transport_graph_get_and_set_node_values(workflow_transport_graph):
    """Test the transport graph node value setting and querying methods."""

    wtg = workflow_transport_graph

    # Raise error since the value key has not been set
    with pytest.raises(KeyError):
        wtg.get_node_value(node_key=0, value_key="mock_value_key")
        wtg.get_node_value(node_key=0, value_key="node_name")

    wtg.set_node_value(node_key=0, value_key="node_name", value="square")
    assert wtg.get_node_value(node_key=0, value_key="node_name") == "square"


def test_transport_graph_get_dependencies(workflow_transport_graph):
    """Test the graph node retrieval method in the transport graph."""

    wtg = workflow_transport_graph
    assert list(wtg.get_dependencies(node_key=0)) == []
    assert list(wtg.get_dependencies(node_key=1)) == []

    # Add edge relation
    wtg.add_edge(x=0, y=1, edge_name="apples")

    assert list(wtg.get_dependencies(node_key=0)) == []
    assert list(wtg.get_dependencies(node_key=1)) == [0]


def test_transport_graph_get_internal_graph_copy(workflow_transport_graph):
    """Test that the graph copying method creates a new graph object."""

    wtg = workflow_transport_graph
    graph = wtg.get_internal_graph_copy()
    assert graph != wtg._graph
    assert isinstance(graph, nx.DiGraph)


def test_transport_graph_serialize(workflow_transport_graph):
    """Test the transport graph serialization method."""

    wtg = workflow_transport_graph
    wtg.add_edge(x=0, y=1, edge_name="apples")
    wtg.lattice_metadata = mock_lattice_metadata = {"mock_lattice_metadata_field": "mock_value"}

    # Check node information is not filtered out when metadata_only is False
    serialized_data = cloudpickle.loads(wtg.serialize(metadata_only=False))
    for field in ["name", "function", "metadata"]:
        assert field in serialized_data["nodes"][0]

    # Check link field "edge_name" is not filtered out when metadata_only is False
    assert "edge_name" in serialized_data["links"][0]

    # Check node information is filtered out when metadata_only is True
    serialized_data = cloudpickle.loads(wtg.serialize(metadata_only=True))
    for _ in range(len(serialized_data["nodes"])):
        assert len(serialized_data["nodes"][0]) == 1
        assert "metadata" in serialized_data["nodes"][0]

    # Check link field "edge_name" is filtered out when metadata_only is True
    assert "edge_name" not in serialized_data["links"][0]

    # Check that parameter nodes get filtered out when metadata_only is True
    wtg.add_node(
        name=f"{parameter_prefix}.param",
        kwargs={"x": 2},
        function=subtask,
        metadata={"mock_field": "mock_value"},
    )
    serialized_data = cloudpickle.loads(wtg.serialize(metadata_only=False))
    assert len(serialized_data["nodes"]) == 3
    assert serialized_data["lattice_metadata"] == mock_lattice_metadata

    serialized_data = cloudpickle.loads(wtg.serialize(metadata_only=True))
    assert len(serialized_data["nodes"]) == 2
    assert serialized_data["lattice_metadata"] == mock_lattice_metadata


def test_transport_graph_deserialize(workflow_transport_graph):
    """Test the transport graph deserialization method."""

    wtg = workflow_transport_graph
    wtg.add_edge(x=0, y=1, edge_name="apples")
    wtg.lattice_metadata = {"mock_lattice_metadata_field": "mock_value"}
    wtg.add_node(
        name=f"{parameter_prefix}.param",
        kwargs={"x": 2},
        function=subtask,
        metadata={"mock_field": "mock_value"},
    )

    serialized_data = cloudpickle.loads(wtg.serialize(metadata_only=False))
    new_mock_lattice_metadata = {"updated_field": "updated_value"}
    serialized_data["lattice_metadata"] = new_mock_lattice_metadata
    wtg.deserialize(pickled_data=cloudpickle.dumps(serialized_data))
    assert wtg.lattice_metadata == new_mock_lattice_metadata

    transportable_obj = wtg.get_node_value(node_key=0, value_key="function")
    assert transportable_obj.get_deserialized()(x=3) == 9
