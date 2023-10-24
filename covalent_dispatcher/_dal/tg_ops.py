# Copyright 2023 Agnostiq Inc.
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

"""Module for transport graph operations."""

from collections import deque
from typing import Callable, List

import networkx as nx

from covalent._shared_files import logger
from covalent._shared_files.util_classes import RESULT_STATUS

from .asset import copy_asset, copy_asset_meta
from .electron import ASSET_KEYS, METADATA_KEYS
from .tg import _TransportGraph

app_log = logger.app_log


class TransportGraphOps:
    def __init__(self, tg: _TransportGraph):
        self.tg = tg
        self._status_map = {1: True, -1: False}

        self._default_node_attrs = {
            "start_time": None,
            "end_time": None,
            "status": RESULT_STATUS.NEW_OBJECT,
            # This will be overwritten by the SDK
            # "output": None,
            # "error": "",
            # "stdout": "",
            # "stderr": "",
        }

    @staticmethod
    def _flag_successors(A: nx.MultiDiGraph, node_statuses: dict, starting_node: int):
        """Flag all successors of a node (including the node itself)."""
        nodes_to_invalidate = [starting_node]
        for node, successors in nx.bfs_successors(A, starting_node):
            nodes_to_invalidate.extend(iter(successors))
        for node in nodes_to_invalidate:
            node_statuses[node] = -1

    @staticmethod
    def is_same_node(A: nx.MultiDiGraph, B: nx.MultiDiGraph, node: int) -> bool:
        """Check if the node attributes are the same in both graphs."""
        return A.nodes[node] == B.nodes[node]

    @staticmethod
    def is_same_edge_attributes(
        A: nx.MultiDiGraph, B: nx.MultiDiGraph, parent: int, node: int
    ) -> bool:
        """Check if the edge attributes are the same in both graphs."""
        return A.adj[parent][node] == B.adj[parent][node]

    def copy_nodes_from(
        self,
        tg: _TransportGraph,
        nodes,
        *,
        copy_metadata: bool = True,
        defer_copy_objects: bool = False,
    ) -> List:
        """Copy nodes from the transport graph in the argument."""

        assets_to_copy = []

        for n in nodes:
            old_node = tg.get_node(n)
            old_status = tg.get_node_value(n, "status")

            if copy_metadata and old_status == RESULT_STATUS.COMPLETED:
                # Only previously completed nodes can actually be
                # reused

                for k in METADATA_KEYS:
                    app_log.debug(f"Copying metadata {k} for node {n}")
                    v = tg.get_node_value(n, k)
                    if k == "status":
                        # This will cause the dispatcher to skip
                        # re-running the node.
                        v = RESULT_STATUS.PENDING_REUSE
                    self.tg.set_node_value(n, k, v)

            # TODO: Use the ElectronAssets link table as the source of
            # truth instead of these hardcoded values
            for k in ASSET_KEYS:
                # Copy asset metadata
                app_log.debug(f"Copying asset {k} for node {n}")
                with old_node.session() as session:
                    old = old_node.get_asset(k, session)
                    new = self.tg.get_node(n).get_asset(k, session)
                    copy_asset_meta(session, old, new)
                    assets_to_copy.append((old, new))

        # Now perform all data copy operations (this could be slow)
        if not defer_copy_objects:
            for item in assets_to_copy:
                src, dest = item
                copy_asset(src, dest)

        # Return the assets to copy at a later time
        return assets_to_copy

    @staticmethod
    def _cmp_name_and_pval(A: nx.MultiDiGraph, B: nx.MultiDiGraph, node: int) -> bool:
        """Default node comparison function for diffing transport graphs.

        Two nodes are considered the "same" if either:
        * both are parameter nodes and have the same hash
        * both are function nodes, have the same name,
          and neither is marked PENDING_REPLACEMENT.
        """

        name_A = A.nodes[node]["name"]
        name_B = B.nodes[node]["name"]

        if name_A != name_B:
            return False

        status_A = A.nodes[node]["status"]
        status_B = B.nodes[node]["status"]
        if (
            status_A == RESULT_STATUS.PENDING_REPLACEMENT
            or status_B == RESULT_STATUS.PENDING_REPLACEMENT
        ):
            return False

        # Same name -- remaining case to check is if both are
        # parameters.  Compare parameter value hashes.
        val_hash_A = A.nodes[node].get("value", None)
        val_hash_B = B.nodes[node].get("value", None)

        return val_hash_A == val_hash_B

    def _max_cbms(
        self,
        A: nx.MultiDiGraph,
        B: nx.MultiDiGraph,
        node_cmp: Callable = None,
        edge_cmp: Callable = None,
    ):
        """Computes a "maximum backward-maximal common subgraph" (cbms)
        Args:
            A: nx.MultiDiGraph
            B: nx.MultiDiGraph
            node_cmp: An optional function for comparing node attributes in A and B.
                    Defaults to testing for equality of the attribute dictionaries
            edge_cmp: An optional function for comparing the edges between two nodes.
                    Defaults to checking that the two sets of edges have the same attributes
        Returns: A_node_status, B_node_status, where each is a dictionary
            `{node: True/False}` where True means reusable.
        Performs a modified BFS of A and B.
        """
        if node_cmp is None:
            node_cmp = self.is_same_node
        if edge_cmp is None:
            edge_cmp = self.is_same_edge_attributes

        A_node_status = {node_id: 0 for node_id in A.nodes}
        B_node_status = {node_id: 0 for node_id in B.nodes}
        app_log.debug(f"A node status: {A_node_status}")
        app_log.debug(f"B node status: {B_node_status}")

        virtual_root = -1

        if virtual_root in A.nodes or virtual_root in B.nodes:
            raise RuntimeError(f"Encountered forbidden node: {virtual_root}")

        assert virtual_root not in B.nodes

        nodes_to_visit = deque()
        nodes_to_visit.appendleft(virtual_root)

        # Add a temporary root
        A_parentless_nodes = [node for node, deg in A.in_degree() if deg == 0]
        B_parentless_nodes = [node for node, deg in B.in_degree() if deg == 0]
        for node_id in A_parentless_nodes:
            A.add_edge(virtual_root, node_id)

        for node_id in B_parentless_nodes:
            B.add_edge(virtual_root, node_id)

        # Assume inductively that predecessors subgraphs are the same;
        # this is satisfied for the root
        while nodes_to_visit:
            current_node = nodes_to_visit.pop()

            app_log.debug(f"Visiting node {current_node}")
            for y in A.adj[current_node]:
                # Don't process already failed nodes
                if A_node_status[y] == -1:
                    continue

                # Check if y is a valid child of current_node in B
                if y not in B.adj[current_node]:
                    app_log.debug(f"A: {y} not adjacent to node {current_node} in B")
                    self._flag_successors(A, A_node_status, y)
                    continue

                if B_node_status[y] == -1:
                    app_log.debug(f"A: Node {y} is marked as failed in B")
                    self._flag_successors(A, A_node_status, y)
                    continue

                # Compare edges
                if not edge_cmp(A, B, current_node, y):
                    app_log.debug(f"Edges between {current_node} and {y} differ")
                    self._flag_successors(A, A_node_status, y)
                    self._flag_successors(B, B_node_status, y)
                    continue

                # Compare nodes
                if not node_cmp(A, B, y):
                    app_log.debug(f"Attributes of node {y} differ:")
                    app_log.debug(f"A[y] = {A.nodes[y]}")
                    app_log.debug(f"B[y] = {B.nodes[y]}")
                    self._flag_successors(A, A_node_status, y)
                    self._flag_successors(B, B_node_status, y)
                    continue

                # Predecessors subgraphs of y are the same in A and B, so
                # enqueue y if it hasn't already been visited
                assert A_node_status[y] != -1
                if A_node_status[y] == 0:
                    A_node_status[y] = 1
                    B_node_status[y] = 1
                    app_log.debug(f"Enqueueing node {y}")
                    nodes_to_visit.appendleft(y)

            # Prune children of current_node in B that aren't valid children in A
            for y in B.adj[current_node]:
                if B_node_status[y] == -1:
                    continue
                if y not in A.adj[current_node]:
                    app_log.debug(f"B: {y} not adjacent to node {current_node} in A")
                    self._flag_successors(B, B_node_status, y)
                    continue
                if B_node_status[y] == -1:
                    app_log.debug(f"B: Node {y} is marked as failed in A")
                    self._flag_successors(B, B_node_status, y)

        A.remove_node(-1)
        B.remove_node(-1)

        app_log.debug(f"A node status: {A_node_status}")
        app_log.debug(f"B node status: {B_node_status}")

        for k, v in A_node_status.items():
            A_node_status[k] = self._status_map[v]
        for k, v in B_node_status.items():
            B_node_status[k] = self._status_map[v]
        return A_node_status, B_node_status

    def get_reusable_nodes(self, tg_new: _TransportGraph) -> List[int]:
        """Find which nodes are common between the current graph and a new graph."""
        A = self.tg.get_internal_graph_copy()
        B = tg_new.get_internal_graph_copy()

        # inject parameter value checksums
        for node_id in A.nodes:
            node = self.tg.get_node(node_id)
            with node.session() as session:
                value_asset = node.get_asset("value", session)
            value_hash = value_asset.digest
            A.nodes[node_id]["value"] = value_hash

        for node_id in B.nodes:
            node = tg_new.get_node(node_id)
            with node.session() as session:
                value_asset = node.get_asset("value", session)
            value_hash = value_asset.digest
            B.nodes[node_id]["value"] = value_hash

        status_A, _ = self._max_cbms(A, B, node_cmp=self._cmp_name_and_pval)
        return [k for k, v in status_A.items() if v]

    def reset_nodes(self):
        """Reset all nodes to be replaced."""
        for node_id in self.tg._graph.nodes:
            status = self.tg.get_node_value(node_id, "status")
            if status == RESULT_STATUS.PENDING_REPLACEMENT:
                self._reset_node(node_id)

    def _reset_node(self, node_id: int) -> None:
        """Reset node values to starting state."""
        node_name = self.tg.get_node_value(node_id, "name")

        for node_attr, default_val in self._default_node_attrs.items():
            self.tg.set_node_value(node_id, node_attr, default_val)
