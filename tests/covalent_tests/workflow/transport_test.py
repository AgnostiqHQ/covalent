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

import covalent as ct
from covalent._shared_files.defaults import parameter_prefix
from covalent._workflow.transport import (
    TransportableObject,
    _TransportGraph,
    encode_metadata,
    max_cbms,
)


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


def test_transportable_object_json_property(transportable_object):
    """Test that TO stores a json rep of json-serializable objects"""

    import json

    jsonable_obj = {"a": 1, "b": 2}
    t = TransportableObject(jsonable_obj)
    assert t.json == json.dumps(jsonable_obj)

    new_t = TransportableObject(t)
    assert new_t.json == ""


def test_transportable_object_eq(transportable_object):
    """Test the __eq__ magic method of TransportableObject"""

    to = transportable_object
    to_new = TransportableObject(None)
    to_new.__dict__ = to.__dict__.copy()
    assert to.__eq__(to_new)

    to_new.python_version = "3.5.1"
    assert not to.__eq__(to_new)

    assert not to.__eq__({})


def test_transportable_object_get_serialized(transportable_object):
    """Test serialized transportable object retrieval."""

    to = transportable_object
    assert to.get_serialized() == to._object


def test_transportable_object_get_deserialized(transportable_object):
    """Test deserialization of the transportable object."""

    to = transportable_object
    assert to.get_deserialized()(x=2) == subtask(x=2)


def test_transportable_object_from_dict(transportable_object):
    to = transportable_object

    object_dict = to.to_dict()

    to_new = TransportableObject.from_dict(object_dict)
    assert to == to_new


def test_transportable_object_serialize_to_json(transportable_object):
    import json

    to = transportable_object
    assert json.dumps(to.to_dict()) == to.serialize_to_json()


def test_transportable_object_deserialize_from_json(transportable_object):
    import json

    to = transportable_object
    json_string = to.serialize_to_json()
    deserialized_to = TransportableObject.deserialize_from_json(json_string)
    assert to.__dict__ == deserialized_to.__dict__


def test_transportable_object_make_transportable_idempotent(transportable_object):
    """Test that `make_transportable` is idempotent"""

    to = transportable_object
    assert TransportableObject.make_transportable(to) == to


def test_transportable_object_serialize_deserialize(transportable_object):
    """Test that the transportable object is unchanged after serialization and deserialization."""

    to = transportable_object
    data = to.serialize()  # Serialize transportable object
    new_to = to.deserialize(data)  # Deserialize transportable object

    assert new_to.get_deserialized()(x=3) == subtask(x=3)
    assert new_to.python_version == to.python_version


def test_transportable_object_deserialize_list(transportable_object):

    deserialized = [1, 2, {"a": 3, "b": [4, 5]}]
    serialized_list = [
        TransportableObject.make_transportable(1),
        TransportableObject.make_transportable(2),
        {
            "a": TransportableObject.make_transportable(3),
            "b": [
                TransportableObject.make_transportable(4),
                TransportableObject.make_transportable(5),
            ],
        },
    ]

    assert TransportableObject.deserialize_list(serialized_list) == deserialized


def test_transportable_object_deserialize_dict(transportable_object):

    deserialized = {"a": 1, "b": [2, {"c": 3}]}
    serialized_dict = {
        "a": TransportableObject.make_transportable(1),
        "b": [
            TransportableObject.make_transportable(2),
            {"c": TransportableObject.make_transportable(3)},
        ],
    }

    assert TransportableObject.deserialize_dict(serialized_dict) == deserialized


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
    wtg.add_edge(x=0, y=1, edge_name="oranges")
    assert wtg._graph.get_edge_data(0, 1) == {
        0: {"edge_name": "apples"},
        1: {"edge_name": "oranges"},
    }


def test_transport_graph_transport_graph_reset(workflow_transport_graph):
    """Test that the transport graph reset method resets the graph."""

    wtg = workflow_transport_graph
    wtg.add_edge(x=0, y=1, edge_name="apples")
    assert list(wtg._graph.nodes) == [0, 1]
    assert list(wtg._graph.edges) == [(0, 1, 0)]
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


def test_transport_graph_json_serialization():
    """Test the transport graph JSON serialization method"""

    import json

    @ct.electron(executor="local", deps_bash=ct.DepsBash("yum install gcc"))
    def f(x):
        return x * x

    @ct.lattice
    def workflow(x):
        return f(x)

    workflow.build_graph(5)
    workflow_tg = workflow.transport_graph

    json_graph = workflow_tg.serialize_to_json()

    tg = _TransportGraph()
    tg.deserialize_from_json(json_graph)

    assert list(workflow_tg._graph.nodes) == list(tg._graph.nodes)

    for node in tg._graph.nodes:
        for k, v in tg._graph.nodes[node].items():
            if k == "metadata":
                continue
            assert v == workflow_tg.get_node_value(node, k)

    # Check that Serialize(Deserialize(Serialize)) == Serialize
    assert json_graph == tg.serialize_to_json()

    json_graph_metadata_only = workflow_tg.serialize_to_json(metadata_only=True)

    # Check node information is filtered out when metadata_only is True
    serialized_data = json.loads(json_graph_metadata_only)
    for _ in range(len(serialized_data["nodes"])):
        assert len(serialized_data["nodes"][0]) == 1
        assert "metadata" in serialized_data["nodes"][0]

    # Check link field "edge_name" is filtered out when metadata_only is True
    assert "edge_name" not in serialized_data["links"][0]


def test_metadata_json_serialization():
    import json

    @ct.electron(executor="local", deps_bash=ct.DepsBash("yum install gcc"))
    def f(x):
        return x * x

    @ct.lattice
    def workflow(x):
        return f(x)

    workflow.build_graph(5)
    workflow_tg = workflow.transport_graph
    metadata = workflow_tg.get_node_value(0, "metadata")

    json_metadata = json.dumps(encode_metadata(metadata))

    new_metadata = json.loads(json_metadata)

    # Check that each metadata type implements its own JSON-serialization
    for k in metadata:
        if k == "executor":
            continue
        if k == "deps":
            for dep_type in metadata[k]:
                if dep_type == "bash":
                    continue
                else:
                    assert metadata[k][dep_type] == new_metadata[k][dep_type]
        else:
            metadata[k] == new_metadata[k]

    assert new_metadata["executor"] == "local"

    new_bash_dep = ct.DepsBash().from_dict(new_metadata["deps"]["bash"])
    assert new_bash_dep.__dict__ == metadata["deps"]["bash"].__dict__


def test_max_cbms():
    """Test function for determining a largest cbms"""

    A = nx.MultiDiGraph()
    B = nx.MultiDiGraph()
    C = nx.MultiDiGraph()
    D = nx.MultiDiGraph()

    #    0     5  6
    #  /  \
    # 1    2
    A.add_edge(0, 1)
    A.add_edge(0, 2)
    A.nodes[1]["color"] = "red"
    A.add_node(5)
    A.add_node(6)

    #    0     5
    #  /  \\
    # 1    2
    B.add_edge(0, 1)
    B.add_edge(0, 2)
    B.add_edge(0, 2)
    B.nodes[1]["color"] = "black"
    B.add_node(5)

    #    0    3
    #  /  \  /
    # 1    2
    C.add_edge(0, 1)
    C.add_edge(0, 2)
    C.add_edge(3, 2)

    #    0    3
    #  /  \  /
    # 1    2
    #     /
    #   4
    D.add_edge(0, 1)
    D.add_edge(0, 2)
    D.add_edge(3, 2)
    D.add_edge(2, 4)

    A_node_status, B_node_status = max_cbms(A, B)
    assert A_node_status == {0: True, 1: False, 2: False, 5: True, 6: False}
    assert B_node_status == {0: True, 1: False, 2: False, 5: True}

    A_node_status, C_node_status = max_cbms(A, C)
    assert A_node_status == {0: True, 1: False, 2: False, 5: False, 6: False}
    assert C_node_status == {0: True, 1: False, 2: False, 3: False}

    C_node_status, D_node_status = max_cbms(C, D)
    assert C_node_status == {0: True, 1: True, 2: True, 3: True}
    assert D_node_status == {0: True, 1: True, 2: True, 3: True, 4: False}


def test_transport_graph_compare():
    """Test method for computing reusable nodes from another transport graph"""

    @ct.electron
    def task_1(x):
        return x

    @ct.electron
    def task_2(x):
        return 2 * x

    @ct.electron
    def task_2a(x, y):
        return x + y

    @ct.electron
    def task_3(x):
        return 3 * x

    #  1 -> 0
    @ct.lattice
    def workflow_1(x):
        res1 = task_1(x)
        return res1

    # 1 -> 0 -> 2
    @ct.lattice
    def workflow_2(x):
        res1 = task_1(x)
        res2 = task_2(res1)
        return res2

    # 1 -> 0 -> 2
    @ct.lattice
    def workflow_3(x):
        res1 = task_1(x)
        res2 = task_3(res1)
        return res2

    #      1  2   5
    #     /    \ /
    #    0      3
    #  /
    # 4
    @ct.lattice
    def workflow_4(x, y, z):
        res1 = task_1(x)
        res2 = task_1(y)
        res3 = task_2(res1)
        res4 = task_2a(res2, z)

    return 1

    workflow_1.build_graph(5)
    workflow_2.build_graph(5)
    workflow_3.build_graph(5)

    tg1 = workflow_1.transport_graph
    tg2 = workflow_2.transport_graph
    tg3 = workflow_3.transport_graph

    assert tg1.compare(tg2) == [0, 1]
    assert tg2.compare(tg2) == [0, 1, 2]
    assert tg2.compare(tg3) == [0, 1]

    workflow_3.build_graph(2)
    tg3 = workflow_3.transport_graph
    assert tg2.compare(tg3) == []

    workflow_4.build_graph(1, 2, 3)
    tg4_1 = workflow_4.transport_graph
    workflow_4.build_graph(1, 2, 4)
    tg4_2 = workflow_4.transport_graph
    workflow_4.build_Graph(1, 3, 3)
    tg4_3 = workflow_4.transport_graph

    assert tg4_1.compare(tg4_2) == [0, 1, 2, 4]
    assert tg4_1.compare(tg4_3) == [0, 1, 4]


def test_transport_graph_compare_meta():
    """Check that tg comparison detects metadata differences"""

    def task(x):
        return x

    task_local = ct.electron(task, executor="local")
    task_dask = ct.electron(task, executor="dask")

    #      1
    #     /
    #    0
    #     \
    #      2
    #       \
    #        3
    @ct.lattice
    def workflow_1(x):
        res1 = task_local(x)
        res2 = task_local(res1)
        return task_dask(res2)

    @ct.lattice
    def workflow_2(x):
        res1 = task_local(x)
        res2 = task_local(res1)
        return task_local(res2)

    workflow_1.build_graph(1)
    workflow_2.build_graph(1)
    tg1 = workflow_1.transport_graph
    tg2 = workflow_2.transport_graph
    assert tg1.compare(tg2) == [0, 1, 2]


def test_transport_graph_compare_edges():
    """Check that tg comparison picks up different edge attributes"""

    @ct.electron
    def task_1(x):
        return x

    @ct.electron
    def task_2(x, y):
        return x + y * y

    #    1       3
    #     \     / (arg)
    #      0   2
    #       \ /
    #        4
    @ct.lattice
    def workflow_1(x, y):
        res1 = task_1(x)
        res2 = task_1(y)
        res3 = task_2(res1, res2)
        return res3

    #    1       3
    #     \     / (kwarg)
    #      0   2
    #   (0) \ / (1)
    #        4
    @ct.lattice
    def workflow_1a(x, y):
        res1 = task_1(x)
        res2 = task_1(y=y)
        res3 = task_2(res1, res2)

    #    1       3
    #     \     / (kwarg)
    #      0   2
    #   (1) \ / (0)
    #        4
    @ct.lattice
    def workflow_2(x, y):
        res1 = task_1(x)
        res2 = task_1(y)
        res3 = task_2(res2, res1)
        return res3

    #    1        3
    #     \      / (kwarg)
    #      0    2
    #       \\
    #        4
    @ct.lattice
    def workflow_3(x, y):
        res1 = task_1(x)
        res2 = task_1(y)
        res3 = task_2(res1, res1)
        return res3

    workflow_1.build_graph(1, 2)
    tg1 = workflow_1.transport_graph
    workflow_1a.build_graph(1, 2)
    tg1a = workflow_1a.transport_graph
    workflow_2.build_graph(1, 2)
    tg2 = workflow_2.transport_graph
    workflow_3.build_graph(1, 2)
    tg3 = workflow_3.transport_graph

    assert list(tg1._graph.nodes) == [0, 1, 2, 3, 4]
    assert tg1.compare(tg1a) == [0, 1]
    assert tg1.compare(tg2) == [0, 1, 2, 3]
    assert tg1.compare(tg3) == [0, 1, 2, 3]
