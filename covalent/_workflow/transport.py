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

"""Class implementation of the transport graph in the workflow graph."""

import datetime
import json
from copy import deepcopy
from typing import Any, Callable, Dict

import cloudpickle
import networkx as nx

from .._shared_files.defaults import parameter_prefix
from .._shared_files.util_classes import RESULT_STATUS, Status
from .transportable_object import TransportableObject


# Functions for encoding the transport graph
def encode_metadata(metadata: dict) -> dict:
    # Idempotent
    # Special handling required for: executor, workflow_executor, deps, call_before/after, triggers

    encoded_metadata = deepcopy(metadata)
    if "executor" in metadata:
        if "executor_data" not in metadata:
            encoded_metadata["executor_data"] = None if metadata["executor"] is None else {}
        if metadata["executor"] is not None and not isinstance(metadata["executor"], str):
            encoded_executor = metadata["executor"].to_dict()
            encoded_metadata["executor"] = encoded_executor["short_name"]
            encoded_metadata["executor_data"] = encoded_executor

    if "workflow_executor" in metadata:
        if "workflow_executor_data" not in metadata:
            encoded_metadata["workflow_executor_data"] = (
                None if metadata["workflow_executor"] is None else {}
            )
        if metadata["workflow_executor"] is not None and not isinstance(
            metadata["workflow_executor"], str
        ):
            encoded_wf_executor = metadata["workflow_executor"].to_dict()
            encoded_metadata["workflow_executor"] = encoded_wf_executor["short_name"]
            encoded_metadata["workflow_executor_data"] = encoded_wf_executor

    # Bash Deps, Pip Deps, Env Deps, etc
    if "deps" in metadata and metadata["deps"] is not None:
        for dep_type, dep_object in metadata["deps"].items():
            if dep_object and not isinstance(dep_object, dict):
                encoded_metadata["deps"][dep_type] = dep_object.to_dict()

    # call_before/after
    if "call_before" in metadata and metadata["call_before"] is not None:
        for i, dep in enumerate(metadata["call_before"]):
            if not isinstance(dep, dict):
                encoded_metadata["call_before"][i] = dep.to_dict()

    if "call_after" in metadata and metadata["call_after"] is not None:
        for i, dep in enumerate(metadata["call_after"]):
            if not isinstance(dep, dict):
                encoded_metadata["call_after"][i] = dep.to_dict()

    # triggers
    if "triggers" in metadata:
        if isinstance(metadata["triggers"], list):
            encoded_metadata["triggers"] = []
            for tr in metadata["triggers"]:
                if isinstance(tr, dict):
                    encoded_metadata["triggers"].append(tr)
                else:
                    encoded_metadata["triggers"].append(tr.to_dict())
        else:
            encoded_metadata["triggers"] = metadata["triggers"]

    # qelectron_data_exists
    encoded_metadata["qelectron_data_exists"] = False

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
        self._graph = nx.MultiDiGraph()
        self.lattice_metadata = None

        # IDs of nodes modified during the workflow run
        self.dirty_nodes = []

        self._default_node_attrs = {
            "start_time": None,
            "end_time": None,
            "status": RESULT_STATUS.NEW_OBJECT,
            "output": TransportableObject(None),
            "error": "",
            "sub_dispatch_id": None,
            "sublattice_result": None,
            "stdout": "",
            "stderr": "",
        }

    def add_node(
        self, name: str, function: Callable, metadata: Dict, task_group_id: int = None, **attr
    ) -> int:
        """
        Adds a node to the graph.

        Args:
            name: The name of the node.
            function: The function to be executed.
            metadata: The metadata of the node.
            task_group_id: The task group id of the node.
            attr: Any other attributes that need to be added to the node.

        Returns:
            node_key: The node id.

        """
        node_id = len(self._graph.nodes)

        if task_group_id is None:
            task_group_id = node_id

        # Default to gid=node_id

        self._graph.add_node(
            node_id,
            task_group_id=task_group_id,
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

    def get_node_value(self, node_key: int, value_key: str) -> Any:
        """
        Get a specific value from a node depending upon the value key.

        Args:
            node_key: The node id.
            value_key: The value key.

        Returns:
            value: The value from the node stored at the value key.

        Raises:
            KeyError: If the value key or node key is not found.
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

    def reset_node(self, node_id: int) -> None:
        """Reset node values to starting state."""
        node_name = self.get_node_value(node_id, "name")

        for node_attr, default_val in self._default_node_attrs.items():
            # Don't clear precomputed parameter outputs.
            if node_attr == "output" and node_name.startswith(parameter_prefix):
                continue

            self.set_node_value(node_id, node_attr, default_val)

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

        Note: serialize_to_json converts metadata objects into dictionary representations.
        """

        # Convert networkx.DiGraph to a format that can be converted to json .
        data = nx.readwrite.node_link_data(self._graph)

        # process each node
        for idx, node in enumerate(data["nodes"]):
            data["nodes"][idx]["function"] = data["nodes"][idx].pop("function").to_dict()
            if "value" in node:
                node["value"] = node["value"].to_dict()
            if "output" in node:
                node["output"] = node["output"].to_dict()
            if "metadata" in node:
                node["metadata"] = encode_metadata(node["metadata"])
            if "start_time" in node:
                if node["start_time"]:
                    node["start_time"] = node["start_time"].isoformat()
            if "end_time" in node:
                if node["end_time"]:
                    node["end_time"] = node["end_time"].isoformat()
            if "status" in node:
                node["status"] = str(node["status"])

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
            if "output" in node:
                node["output"] = TransportableObject.from_dict(node["output"])
            if "start_time" in node:
                if node["start_time"]:
                    node["start_time"] = datetime.datetime.fromisoformat(node["start_time"])
            if "end_time" in node:
                if node["end_time"]:
                    node["end_time"] = datetime.datetime.fromisoformat(node["end_time"])
            if "status" in node:
                node["status"] = Status(node["status"])

        self._graph = nx.readwrite.node_link_graph(node_link_data)
