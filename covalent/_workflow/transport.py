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
import json
import platform
from copy import deepcopy
from typing import Any, Callable, Dict, List

import cloudpickle
import networkx as nx

from .._data_store import DataStoreSession, models
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

        self.object_string = str(obj)

        try:
            self._json = json.dumps(obj)

        except TypeError as ex:
            self._json = ""

        self.attrs = {"doc": getattr(obj, "doc", ""), "name": getattr(obj, "name", "")}

    def __eq__(self, obj) -> bool:
        if not isinstance(obj, TransportableObject):
            return False
        return self.__dict__ == obj.__dict__

    def get_deserialized(self) -> Callable:
        """
        Get the deserialized transportable object.

        Args:
            None

        Returns:
            function: The deserialized object/callable function.

        """

        return cloudpickle.loads(base64.b64decode(self._object.encode("utf-8")))

    @property
    def json(self):
        return self._json

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary representation of self"""
        return {"type": "TransportableObject", "attributes": self.__dict__.copy()}

    @staticmethod
    def from_dict(object_dict) -> "TransportableObject":
        """Rehydrate a dictionary representation

        Args:
            object_dict: a dictionary representation returned by `to_dict`

        Returns:
            A `TransportableObject` represented by `object_dict`
        """

        sc = TransportableObject(None)
        sc.__dict__ = object_dict["attributes"]
        return sc

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
            {
                "object": self.get_serialized(),
                "object_string": self.object_string,
                "json": self._json,
                "attrs": self.attrs,
                "py_version": self.python_version,
            }
        )

    def serialize_to_json(self) -> str:
        """
        Serialize the transportable object to JSON.

        Args:
            None

        Returns:
            A JSON string representation of the transportable object
        """

        return json.dumps(self.to_dict())

    @staticmethod
    def deserialize_from_json(json_string: str) -> str:
        """
        Reconstruct a transportable object from JSON

        Args:
            json_string: A JSON string representation of a TransportableObject

        Returns:
            A TransportableObject instance
        """

        object_dict = json.loads(json_string)
        return TransportableObject.from_dict(object_dict)

    @staticmethod
    def make_transportable(obj) -> "TransportableObject":
        if isinstance(obj, TransportableObject):
            return obj
        else:
            return TransportableObject(obj)

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
        sc._json = obj["json"]
        sc.attrs = obj["attrs"]
        sc.python_version = obj["py_version"]
        return sc

    @staticmethod
    def deserialize_list(collection: list) -> list:
        """
        Recursively deserializes a list of TransportableObjects. More
        precisely, `collection` is a list, each of whose entries is
        assumed to be either a `TransportableObject`, a list, or dict`
        """

        new_list = []
        for item in collection:
            if isinstance(item, TransportableObject):
                new_list.append(item.get_deserialized())
            elif isinstance(item, list):
                new_list.append(TransportableObject.deserialize_list(item))
            elif isinstance(item, dict):
                new_list.append(TransportableObject.deserialize_dict(item))
            else:
                raise TypeError("Couldn't deserialize collection")
        return new_list

    @staticmethod
    def deserialize_dict(collection: dict) -> dict:
        """
        Recursively deserializes a dict of TransportableObjects. More
        precisely, `collection` is a dict, each of whose entries is
        assumed to be either a `TransportableObject`, a list, or dict`

        """

        new_dict = {}
        for k, item in collection.items():
            if isinstance(item, TransportableObject):
                new_dict[k] = item.get_deserialized()
            elif isinstance(item, list):
                new_dict[k] = TransportableObject.deserialize_list(item)
            elif isinstance(item, dict):
                new_dict[k] = TransportableObject.deserialize_dict(item)
            else:
                raise TypeError("Couldn't deserialize collection")
        return new_dict


# Functions for encoding the transport graph


def encode_metadata(metadata: dict) -> dict:
    # Idempotent
    # Special handling required for: executor, workflow_executor, deps, call_before/after

    encoded_metadata = deepcopy(metadata)
    if "executor" in metadata:
        if "executor_data" not in metadata:
            encoded_metadata["executor_data"] = {}
        if not isinstance(metadata["executor"], str):
            encoded_executor = metadata["executor"].to_dict()
            encoded_metadata["executor"] = encoded_executor["short_name"]
            encoded_metadata["executor_data"] = encoded_executor

    if "workflow_executor" in metadata:
        if "workflow_executor_data" not in metadata:
            encoded_metadata["workflow_executor_data"] = {}
        if not isinstance(metadata["workflow_executor"], str):
            encoded_wf_executor = metadata["workflow_executor"].to_dict()
            encoded_metadata["workflow_executor"] = encoded_wf_executor["short_name"]
            encoded_metadata["workflow_executor_data"] = encoded_wf_executor

    # Bash Deps, Pip Deps, Env Deps, etc
    if "deps" in metadata:
        for dep_type, dep_object in metadata["deps"].items():
            if not isinstance(dep_object, dict):
                encoded_metadata["deps"][dep_type] = dep_object.to_dict()

    # call_before/after
    if "call_before" in metadata:
        for i, dep in enumerate(metadata["call_before"]):
            if not isinstance(dep, dict):
                encoded_metadata["call_before"][i] = dep.to_dict()

    if "call_after" in metadata:
        for i, dep in enumerate(metadata["call_after"]):
            if not isinstance(dep, dict):
                encoded_metadata["call_after"][i] = dep.to_dict()

    return encoded_metadata


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
        # Edge insertion order is not preserved in networkx. So manually persist it
        # using 'edge_insertion_order' attribute.
        self._graph = nx.MultiDiGraph(edge_insertion_order=[])
        self.lattice_metadata = None

        # IDs of nodes modified during the workflow run
        self.dirty_nodes = []

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
        Adds an edge to the graph and assigns a name to it. Edge insertion
        order is not preserved in networkx. So in case of positional arguments
        passed into the electron, we need to preserve the order when we
        deserialize the request in the lattice.

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

        self._graph.graph["edge_insertion_order"].append(x)
        self._graph.add_edge(x, y, edge_name=edge_name, **attr)

    def reset(self) -> None:
        """
        Resets the graph.

        Args:
            None

        Returns:
            None
        """

        self._graph = nx.MultiDiGraph(edge_insertion_order=[])

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

        self.dirty_nodes.append(node_key)
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

    def serialize_to_json(self, metadata_only: bool = False) -> str:
        """
        Convert transport graph object to JSON to be used in the workflow scheduler.

        Convert transport graph networkx.DiGraph object into JSON format, filter out
        computation specific attributes and lastly add the lattice metadata. This also
        serializes the function Callable into by base64 encoding the cloudpickled result.

        Args:
            metadata_only: If true, only serialize the metadata.

        Returns:
            str: json string representation of transport graph

        Note: serialize_to_json converts metadata objects into dictionary represetations.
        """

        # Convert networkx.DiGraph to a format that can be converted to json .
        data = nx.readwrite.node_link_data(self._graph)

        # process each node
        for idx, node in enumerate(data["nodes"]):
            data["nodes"][idx]["function"] = data["nodes"][idx].pop("function").to_dict()
            if "value" in node:
                node["value"] = node["value"].to_dict()
            if "metadata" in node:
                node["metadata"] = encode_metadata(node["metadata"])

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

        data["lattice_metadata"] = encode_metadata(self.lattice_metadata)
        return json.dumps(data)

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
        self.sort_edges_based_on_insertion_order()

    def deserialize_from_json(self, json_data: str) -> None:
        """Load JSON representation of transport graph into the transport graph instance.

        This overwrites anything currently set in the transport
        graph. Note that metadata (node and lattice-level) need to be
        reconstituted from their dictionary representations when
        needed.

        Args:
            json_data: JSON representation of the transport graph

        Returns:
            None

        """

        node_link_data = json.loads(json_data)
        if "lattice_metadata" in node_link_data:
            self.lattice_metadata = node_link_data["lattice_metadata"]

        for idx, node in enumerate(node_link_data["nodes"]):
            function_ser = node_link_data["nodes"][idx].pop("function")
            node_link_data["nodes"][idx]["function"] = TransportableObject.from_dict(function_ser)
            if "value" in node:
                node["value"] = TransportableObject.from_dict(node["value"])

        self._graph = nx.readwrite.node_link_graph(node_link_data)
        self.sort_edges_based_on_insertion_order()

    def sort_edges_based_on_insertion_order(self):
        unsorted_edges = list(self._graph.edges(data=True))
        insertion_order = self._graph.graph["edge_insertion_order"]
        unsorted_edges_position_index = [insertion_order.index(i[0]) for i in unsorted_edges]
        unsorted_index_map = zip(unsorted_edges_position_index, unsorted_edges)
        sorted_edge_list_with_index = sorted(unsorted_index_map, key=lambda x: x[0])
        sorted_edge_list = [i[1] for i in sorted_edge_list_with_index]

        # Creates graph without any edges.
        self._graph = nx.create_empty_copy(self._graph)
        # Updates the graph with the edges.
        self._graph.update(edges=sorted_edge_list)

    def persist(self, ds: DataStoreSession, update: bool):
        if update:
            for node_id in self.dirty_nodes:
                self.persist_node(ds, node_id)
            self.dirty_nodes.clear()
        else:
            # Save all nodes and edges
            for node_id in self._graph.nodes:
                self.persist_node(ds, node_id)
            for edge in self._graph.edges:
                self.persist_edge(ds, edge[0], edge[1])
            self.dirty_nodes.clear()

    def persist_node(self, ds: DataStoreSession, node_id: int):
        dispatch_id = ds.metadata["dispatch_id"]
        raise NotImplementedError

    def persist_edge(self, ds: DataStoreSession, parent_id: int, node_id: int):
        dispatch_id = ds.metadata["dispatch_id"]
        raise NotImplementedError
