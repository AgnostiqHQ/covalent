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

"""Unit tests for transport graph."""

import base64
import json
import platform
from unittest.mock import call

import cloudpickle
import networkx as nx
import pytest

import covalent as ct
from covalent._shared_files.defaults import parameter_prefix
from covalent._workflow.transport import (
    TransportableObject,
    _TransportGraph,
    add_module_deps_to_lattice_metadata,
    encode_metadata,
    pickle_modules_by_value,
)
from covalent._workflow.transportable_object import (
    BYTE_ORDER,
    DATA_OFFSET_BYTES,
    STRING_OFFSET_BYTES,
)
from covalent.executor import LocalExecutor
from covalent.triggers import BaseTrigger


def subtask(x):
    """Workflow subtask."""

    return x**2


def subtask_2(x):
    """Workflow subtask 2."""

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


# For testing TObj back-compat -- copied from earlier SDK
class _TOArchive:
    """Archived transportable object."""

    def __init__(self, header: bytes, object_string: bytes, data: bytes):
        """
        Initialize TOArchive.

        Args:
            header: Archived transportable object header.
            object_string: Archived transportable object string.
            data: Archived transportable object data.

        Returns:
            None
        """

        self.header = header
        self.object_string = object_string
        self.data = data

    def cat(self) -> bytes:
        """
        Concatenate TOArchive.

        Returns:
            Concatenated TOArchive.

        """

        header_size = len(self.header)
        string_size = len(self.object_string)
        data_offset = STRING_OFFSET_BYTES + DATA_OFFSET_BYTES + header_size + string_size
        string_offset = STRING_OFFSET_BYTES + DATA_OFFSET_BYTES + header_size

        data_offset = data_offset.to_bytes(DATA_OFFSET_BYTES, BYTE_ORDER, signed=False)
        string_offset = string_offset.to_bytes(STRING_OFFSET_BYTES, BYTE_ORDER, signed=False)

        return string_offset + data_offset + self.header + self.object_string + self.data


# Copied from previous SDK version
class LegacyTransportableObject:
    """
    A function is converted to a transportable object by serializing it using cloudpickle
    and then whenever executing it, the transportable object is deserialized. The object
    will also contain additional info like the python version used to serialize it.

    Attributes:
        _object: The serialized object.
        python_version: The python version used on the client's machine.
    """

    def __init__(self, obj) -> None:
        b64object = base64.b64encode(cloudpickle.dumps(obj))
        object_string_u8 = str(obj).encode("utf-8")

        self._object = b64object.decode("utf-8")
        self._object_string = object_string_u8.decode("utf-8")

        self._header = {
            "py_version": platform.python_version(),
            "cloudpickle_version": cloudpickle.__version__,
            "attrs": {
                "doc": getattr(obj, "__doc__", ""),
                "name": getattr(obj, "__name__", ""),
            },
        }

    # For testing TObj back-compat
    @staticmethod
    def _to_archive(to) -> _TOArchive:
        """
        Convert a TransportableObject to a _TOArchive.

        Args:
            to: Transportable object to be converted.

        Returns:
            Archived transportable object.

        """

        header = json.dumps(to._header).encode("utf-8")
        object_string = to._object_string.encode("utf-8")
        data = to._object.encode("utf-8")
        return _TOArchive(header=header, object_string=object_string, data=data)

    def serialize(self) -> bytes:
        """
        Serialize the transportable object.

        Args:
            None

        Returns:
            pickled_object: The serialized object alongwith the python version.
        """

        return LegacyTransportableObject._to_archive(self).cat()


def test_transportable_object_python_version(transportable_object):
    """Test that the transportable object retrieves the correct python version."""

    to = transportable_object
    assert to.python_version == platform.python_version()


def test_transportable_object_eq():
    """Test the __eq__ magic method of TransportableObject"""

    to = TransportableObject(1)
    to_new = TransportableObject(1)
    to_new_2 = TransportableObject(2)
    assert to == to_new
    assert to != to_new_2
    assert to != 1


def test_transportable_object_get_serialized(transportable_object):
    """Test serialized transportable object retrieval."""

    to = transportable_object
    assert to.get_serialized() == base64.b64encode(cloudpickle.dumps(subtask)).decode("utf-8")


def test_transportable_object_get_deserialized(transportable_object):
    """Test deserialization of the transportable object."""

    to = transportable_object
    assert to.get_deserialized()(x=2) == subtask(x=2)


def test_transportable_object_from_dict(transportable_object):
    to = transportable_object

    object_dict = to.to_dict()

    to_new = TransportableObject.from_dict(object_dict)
    assert to == to_new
    assert to_new.header == to.header
    assert to_new.object_string == to.object_string


def test_transportable_object_serialize_to_json(transportable_object):
    import json

    to = transportable_object
    assert json.dumps(to.to_dict()) == to.serialize_to_json()


def test_transportable_object_deserialize_from_json(transportable_object):
    import json

    to = transportable_object
    json_string = to.serialize_to_json()
    deserialized_to = TransportableObject.deserialize_from_json(json_string)
    assert to == deserialized_to
    assert deserialized_to.header == to.header
    assert deserialized_to.object_string == to.object_string


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


def test_tobj_deserialize_back_compat():
    lto = LegacyTransportableObject({"a": 5})
    serialized = lto.serialize()
    to = TransportableObject.deserialize(serialized)
    obj = to.get_deserialized()
    assert obj == {"a": 5}
    obj2 = TransportableObject.deserialize(to.serialize()).get_deserialized()
    assert obj2 == {"a": 5}


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
    assert not list(wtg._graph.nodes)
    assert not list(wtg._graph.edges)


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
    assert not list(wtg.get_dependencies(node_key=0))
    assert not list(wtg.get_dependencies(node_key=1))

    # Add edge relation
    wtg.add_edge(x=0, y=1, edge_name="apples")

    assert not list(wtg.get_dependencies(node_key=0))
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

    import datetime
    import json

    @ct.electron(executor="local", deps_bash=ct.DepsBash("yum install gcc"))
    def f(x):
        return x * x

    @ct.lattice
    def workflow(x):
        return f(x)

    workflow.build_graph(5)
    workflow_tg = workflow.transport_graph
    ts = datetime.datetime.now((datetime.timezone.utc))

    workflow_tg.set_node_value(1, "start_time", ts)
    workflow_tg.set_node_value(1, "end_time", ts)
    workflow_tg.set_node_value(1, "status", ct.status.COMPLETED)

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

    # Check timestamps
    assert tg.get_node_value(1, "start_time") == ts
    assert tg.get_node_value(1, "end_time") == ts

    # Check status
    assert tg.get_node_value(1, "status") == ct.status.COMPLETED


def test_encode_metadata():
    """Test function to JSON-serialize electron metadata"""

    import json

    le = LocalExecutor()
    bt = BaseTrigger()

    hooks = {
        "deps": {
            "bash": ct.DepsBash("yum install gcc"),
            "pip": ct.DepsPip(["sklearn"]),
        },
        "call_before": [],
        "call_after": [],
    }
    metadata = {"executor": le, "workflow_executor": "local", "hooks": hooks}
    metadata["triggers"] = [bt]

    json_metadata = json.dumps(encode_metadata(metadata))

    new_metadata = json.loads(json_metadata)

    assert new_metadata["executor"] == "local"
    assert new_metadata["executor_data"] == le.to_dict()
    assert new_metadata["workflow_executor"] == "local"
    assert new_metadata["workflow_executor_data"] == {}
    assert new_metadata["triggers"] == [bt.to_dict()]

    assert ct.DepsBash("yum install gcc").to_dict() == new_metadata["hooks"]["deps"]["bash"]
    assert ct.DepsPip(["sklearn"]).to_dict() == new_metadata["hooks"]["deps"]["pip"]

    # Check idempotence
    assert encode_metadata(metadata) == encode_metadata(encode_metadata(metadata))


def test_reset_node(workflow_transport_graph, mocker):
    """Test the node reset method."""
    set_node_value_mock = mocker.patch(
        "covalent._workflow.transport._TransportGraph.set_node_value"
    )

    node_id = 0
    workflow_transport_graph.reset_node(node_id)
    actual_mock_calls = set_node_value_mock.mock_calls
    expected_mock_calls = [
        call(node_id, node_attr, default_val)
        for node_attr, default_val in workflow_transport_graph._default_node_attrs.items()
    ]

    for mock_call in expected_mock_calls:
        assert mock_call in actual_mock_calls


@pytest.mark.parametrize(
    ["call_before", "metadata", "expected_metadata"],
    [
        ([], {}, {}),
        (
            [ct.DepsModule("isort").to_dict()],
            {"hooks": {"call_before": [ct.DepsModule("isort").to_dict()]}},
            {"hooks": {"call_before": []}},
        ),
    ],
)
def test_pickle_modules_by_value(mocker, call_before, metadata, expected_metadata):
    """
    Test that the modules mentioned in
    DepsModules are pickled by value.
    """
    import isort

    mock_cloudpickle = mocker.patch("covalent._workflow.transport.cloudpickle")

    with pickle_modules_by_value(metadata) as received_metadata:
        assert received_metadata == expected_metadata

    if call_before:
        mock_cloudpickle.register_pickle_by_value.assert_called_once_with(isort)
        mock_cloudpickle.unregister_pickle_by_value.assert_called_once_with(isort)


def test_add_module_deps_to_lattice_metadata(mocker):
    """
    Test that the modules mentioned in
    DepsModules are added to the lattice metadata temporarily.
    """

    pp = mocker.Mock()
    pp.lattice.metadata = {"hooks": {"call_before": []}}

    mock_call_before = [ct.DepsModule("isort").to_dict()]

    mock_electron = mocker.Mock()
    mock_electron.metadata = {"hooks": {"call_before": mock_call_before.copy()}}

    mock_bound_electrons = {0: mock_electron}

    with add_module_deps_to_lattice_metadata(pp, mock_bound_electrons):
        assert pp.lattice.metadata["hooks"]["call_before"] == mock_call_before

    assert pp.lattice.metadata["hooks"]["call_before"] == []
