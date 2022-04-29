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

"""Class implementation of the transport graph in the workflow graph."""

import base64
import platform
from typing import Any, Callable, Dict, List

import cloudpickle
import networkx as nx

from .._shared_files.defaults import parameter_prefix


class TransportableObject:
    """
    A function is converted to a transportable object by serializing it using cloudpickle
    and then whenever executing it, the transportable object is deserialized. The object
    will also contain additional info like the python version used to serialize it.

    Attributes:
        _object: The serialized object.
        python_version: The python version used on the client's machine.
    """

    def __init__(self, obj: Any) -> None:
        self._object = base64.b64encode(cloudpickle.dumps(obj)).decode("utf-8")
        self.python_version = platform.python_version()

    def get_deserialized(self) -> Callable:
        """
        Get the deserialized transportable object.

        Args:
            None

        Returns:
            function: The deserialized object/callable function.

        """

        return cloudpickle.loads(base64.b64decode(self._object.encode("utf-8")))

    def get_serialized(self) -> str:
        """
        Get the serialized transportable object.

        Args:
            None

        Returns:
            object: The serialized transportable object.
        """

        return self._object

    def serialize(self) -> bytes:
        """
        Serialize the transportable object.

        Args:
            None

        Returns:
            pickled_object: The serialized object alongwith the python version.
        """

        return cloudpickle.dumps(
            {"object": self.get_serialized(), "py_version": self.python_version}
        )

    @staticmethod
    def deserialize(data: bytes) -> "TransportableObject":
        """
        Deserialize the transportable object.

        Args:
            data: Cloudpickled function.

        Returns:
            object: The deserialized transportable object.
        """

        obj = cloudpickle.loads(data)
        sc = TransportableObject(None)
        sc._object = obj["object"]
        sc.python_version = obj["py_version"]
        return sc


class _TransportGraph:
    """
    A TransportGraph is the most essential part of the whole workflow. This contains
    all the information about each electron and lattice required for determining how,
    when, and where to execute the workflow. The TransportGraph contains a directed graph
    which is used to determine the execution order of the nodes. Each node in this graph
    is an electron which is ready to be executed.

    Attributes:
        _graph: The directed graph object of type networkx.DiGraph().
        lattice_metadata: The lattice metadata of the transport graph.
    """

    def __init__(self) -> None:
        self._graph = nx.MultiDiGraph()
        self.lattice_metadata = None

    def add_node(self, name: str, function: Callable, metadata: Dict, **attr) -> int:
        """
        Adds a node to the graph.

        Args:
            name: The name of the node.
            function: The function to be executed.
            metadata: The metadata of the node.
            attr: Any other attributes that need to be added to the node.

        Returns:
            node_key: The node id.
        """

        node_id = len(self._graph.nodes)
        self._graph.add_node(
            node_id,
            name=name,
            function=TransportableObject(function),
            metadata=metadata,
            **attr,
        )
        return node_id

    def add_edge(self, x: int, y: int, edge_name: Any, **attr) -> None:
        """
        Adds an edge to the graph and assigns a name to it.

        Args:
            x: The node id for first node.
            y: The node id for second node.
            edge_name: The name to be assigned to the edge.
            attr: Any other attributes that need to be added to the edge.

        Returns:
            None

        Raises:
            ValueError: If the edge already exists.
        """

        self._graph.add_edge(x, y, edge_name=edge_name, **attr)

    def reset(self) -> None:
        """
        Resets the graph.

        Args:
            None

        Returns:
            None
        """

        self._graph = nx.MultiDiGraph()

    def get_topologically_sorted_graph(self) -> List[List[int]]:
        """
        Generates a list of node ids in the hierarchical
        order of their position in the graph. Taking care
        of dependencies of each node. Allows for parrallel
        execution of nodes which are at the same level.

        Args:
            None

        Returns:
            sorted_nodes: List of node ids where nodes
                          belonging to the same level are
                          grouped together.
        """

        _g = self._graph.copy()
        res = []
        while _g:
            zero_indegree = [v for v, d in _g.in_degree() if d == 0]
            res.append(zero_indegree)
            _g.remove_nodes_from(zero_indegree)
        return res

    def get_node_value(self, node_key: int, value_key: str) -> Any:
        """
        Get a specific value from a node depending upon the value key.

        Args:
            node_key: The node id.
            value_key: The value key.

        Returns:
            value: The value from the node stored at the value key.

        Raises:
            KeyError: If the value key is not found.
        """

        return self._graph.nodes[node_key][value_key]

    def set_node_value(self, node_key: int, value_key: int, value: Any) -> None:
        """
        Set a certain value of a node. This allows for saving custom data
        in the graph nodes.

        Args:
            node_key: The node id.
            value_key: The value key.
            value: The value to be set at value_key position of the node.

        Returns:
            None

        Raises:
            KeyError: If the node key is not found.
        """

        self._graph.nodes[node_key][value_key] = value

    def get_edge_data(self, dep_key: int, node_key: int) -> Any:
        """
        Get the metadata for all edges between two nodes.

        Args:
            dep_key: The node id for first node.
            node_key: The node id for second node.

        Returns:
            values: A dict {edge_key : value}

        Raises:
            KeyError: If the edge is not found.
        """

        return self._graph.get_edge_data(dep_key, node_key)

    def get_dependencies(self, node_key: int) -> list:
        """
        Gets the parent node ids of a node.

        Args:
            node_key: The node id.

        Returns:
            parents: The dependencies of the node.
        """

        return list(self._graph.predecessors(node_key))

    def get_internal_graph_copy(self) -> nx.MultiDiGraph:
        """
        Get a copy of the internal directed graph
        to avoid modifying the original graph.

        Args:
            None

        Returns:
            graph: A copy of the internal directed graph.
        """

        return self._graph.copy()

    def serialize(self, metadata_only: bool = False) -> bytes:
        """
        Convert transport graph object to JSON to be used in the workflow scheduler.

        Convert transport graph networkx.DiGraph object into JSON format, filter out
        computation specific attributes and lastly add the lattice metadata. This also
        serializes the function Callable into by base64 encoding the cloudpickled result.

        Args:
            metadata_only: If true, only serialize the metadata.

        Returns:
            str: json string representation of transport graph
        """

        # Convert networkx.DiGraph to a format that can be converted to json .
        data = nx.readwrite.node_link_data(self._graph)

        # process each node
        for idx, node in enumerate(data["nodes"]):
            data["nodes"][idx]["function"] = data["nodes"][idx].pop("function").serialize()

        if metadata_only:
            parameter_node_id = [
                i
                for i, node in enumerate(data["nodes"])
                if node["name"].startswith(parameter_prefix)
            ]

            for node in data["nodes"].copy():
                if node["id"] in parameter_node_id:
                    data["nodes"].remove(node)

            # Remove the non-metadata fields such as 'function', 'name', etc from the scheduler workflow input data.
            for idx, node in enumerate(data["nodes"]):
                for field in data["nodes"][idx].copy():
                    if field != "metadata":
                        data["nodes"][idx].pop(field, None)

            # Remove the non-source-target fields from the scheduler workflow input data.
            for idx, node in enumerate(data["links"]):
                for name in data["links"][idx].copy():
                    if name not in ["source", "target"]:
                        data["links"][idx].pop("edge_name", None)

        data["lattice_metadata"] = self.lattice_metadata
        return cloudpickle.dumps(data)

    def deserialize(self, pickled_data: bytes) -> None:
        """
        Load pickled representation of transport graph into the transport graph instance.

        This overwrites anything currently set in the transport graph and deserializes
        the base64 encoded cloudpickled function into a Callable.

        Args:
            pickled_data: Cloudpickled representation of the transport graph

        Returns:
            None
        """

        node_link_data = cloudpickle.loads(pickled_data)
        if "lattice_metadata" in node_link_data:
            self.lattice_metadata = node_link_data["lattice_metadata"]

        for idx, _ in enumerate(node_link_data["nodes"]):
            function_ser = node_link_data["nodes"][idx].pop("function")
            node_link_data["nodes"][idx]["function"] = TransportableObject.deserialize(
                function_ser
            )
        self._graph = nx.readwrite.node_link_graph(node_link_data)
