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

"""DB-backed electron"""

from typing import Any, Dict, List, Tuple

import networkx as nx
from sqlalchemy.orm import Session

from covalent._shared_files import logger

from .._db.datastore import workflow_db
from .._db.models import Electron as ElectronRecord
from .._db.models import ElectronDependency as EdgeRecord
from .db_interfaces.tg_utils import (
    _all_edge_records,
    _child_records,
    _edge_records_for_nodes,
    _incoming_edge_records,
    _node_record,
    _node_records,
)
from .edge import Edge
from .electron import Electron as Node

app_log = logger.app_log


class _TransportGraph:
    def __init__(self, lattice_id: int, bare: bool = False):
        self.lattice_id = lattice_id
        self.bare = bare
        self._nodes = {}
        self._graph = nx.MultiDiGraph()

    def add_node(self, node: Node):
        self._graph.add_node(node.node_id, **node.pure_metadata)
        self._nodes[node.node_id] = node

    def add_edge(self, x: int, y: int, **attrs):
        self._graph.add_edge(x, y, **attrs)

    def get_node(self, node_id: int, session: Session = None) -> Node:
        if not self.bare:
            return self._nodes[node_id]

        # Construct node from db
        if session:
            node = _node(session, self.lattice_id, node_id)
        else:
            with workflow_db.session() as session:
                node = _node(session, self.lattice_id, node_id)
        return node

    def get_node_value(
        self, node_id: int, key: str, session: Session = None, refresh: bool = True
    ):
        node = self.get_node(node_id, session)
        return node.get_value(key, session, refresh)

    def get_node_values(
        self, node_id: int, keys: List[str], session: Session = None, refresh: bool = True
    ):
        node = self.get_node(node_id, session)
        return node.get_values(keys, session, refresh)

    def set_node_values(
        self, node_id: int, keyvals: List[Tuple[str, Any]], session: Session = None
    ):
        node = self.get_node(node_id, session)
        node.set_values(keyvals, session)

    def set_node_value(self, node_id: int, key: str, val: Any, session: Session = None):
        node = self.get_node(node_id, session)
        node.set_value(key, val, session)

    def get_incoming_edges(self, node_id: int) -> List[Tuple[int, int, Dict]]:
        # Read from internal NX graph
        if not self.bare:
            pred = list(self._graph.predecessors(node_id))
            edge_list = [
                {"source": s, "target": node_id, "attrs": d}
                for s in pred
                for _, d in self.get_edge_data(s, node_id).items()
            ]
            return edge_list

        # Read from DB
        with workflow_db.session() as session:
            node = self.get_node(node_id, session)
            edge_list = _get_incoming_edges(session, node)
            return list(
                map(
                    lambda e: {"source": e.source, "target": e.target, "attrs": e.attrs}, edge_list
                )
            )

    def get_successors(self, node_id: int, attr_keys: List = []) -> List[Dict]:
        """Get child nodes with multiplicity"""

        # Read from internal NX graph
        if not self.bare:
            node_list = [
                self.get_node(child)
                for child, edges in self._graph.adj[node_id].items()
                for edge in edges
            ]
            return _filter_node_list(node_list, None, attr_keys)

        # Query DB
        with workflow_db.session() as session:
            node = self.get_node(node_id, session)
            child_node_list = _get_child_nodes(session, node)
            return _filter_node_list(child_node_list, session, attr_keys)

    # Copied from _TransportGraph
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

        if not self.bare:
            return self._graph.get_edge_data(dep_key, node_key)

        with workflow_db.session() as session:
            source = self.get_node(dep_key, session)
            target = self.get_node(node_key, session)
            return _get_edge_data_for_nodes(session, source, target)

    def get_internal_graph_copy(self) -> nx.MultiDiGraph:
        return self._graph.copy()

    def get_dependencies(self, node_key: int) -> list:
        """Gets the parent node ids of a node with multiplicity

        Args:
            node_key: The node id.

        Returns: parents: The dependencies of the node. Parent nodes
            are repeated according to edge multiplicity.

        """
        return [e["source"] for e in self.get_incoming_edges(node_key)]


def _get_incoming_edges(session: Session, node: Node) -> List[Edge]:
    records = _incoming_edge_records(session, node._electron_id)
    nodes = list(map(lambda r: _to_node(session, r[0]), records))
    uid_node_id_map = {n._electron_id: n.node_id for n in nodes}
    uid_node_id_map[node._electron_id] = node.node_id
    edge_list = list(map(lambda r: _to_edge(r[1], uid_node_id_map), records))

    return edge_list


def _get_child_nodes(session: Session, node: Node) -> List[Node]:
    """Return successor nodes with multiplicity"""
    records = _child_records(session, node._electron_id)
    return list(map(lambda r: _to_node(session, r), records))


def _to_node(session: Session, record: ElectronRecord) -> Node:
    return Node(session, record)


def _to_edge(e_record: EdgeRecord, uid_node_id_map: Dict) -> Edge:
    return Edge(e_record, uid_node_id_map)


def _node(session: Session, lattice_id: int, node_id: int) -> Node:
    return _to_node(session, _node_record(session, lattice_id, node_id))


def _get_edge_data_for_nodes(session: Session, parent_node: Node, child_node: Node):
    records = _edge_records_for_nodes(session, parent_node._electron_id, child_node._electron_id)

    uid_node_id_map = {
        child_node._electron_id: child_node.node_id,
        parent_node._electron_id: parent_node.node_id,
    }
    edge_list = list(map(lambda r: _to_edge(r, uid_node_id_map), records))

    return {i: e.attrs for i, e in enumerate(edge_list)}


def _nodes_and_edges(session: Session, lattice_id: int) -> Tuple[List[Node], List[Edge]]:

    db_nodes = _node_records(session, lattice_id)
    db_edges = _all_edge_records(session, lattice_id)
    uid_nodeid_map = {e.id: e.transport_graph_node_id for e in db_nodes}
    nodes = list(map(lambda x: _to_node(session, x), db_nodes))
    edges = list(map(lambda x: _to_edge(x, uid_nodeid_map), db_edges))

    return nodes, edges


def _make_compute_graph(lattice_id: int, nodes: List, edges: List) -> _TransportGraph:
    tg = _TransportGraph(lattice_id)
    for node in nodes:
        tg.add_node(node)
    for edge in edges:
        tg.add_edge(edge.source, edge.target, **edge.attrs)
    return tg


def get_compute_graph(lattice_id: int, bare: bool = False) -> _TransportGraph:
    if not bare:
        with workflow_db.Session() as session:
            nodes, edges = _nodes_and_edges(session, lattice_id)
        return _make_compute_graph(lattice_id, nodes, edges)
    else:
        app_log.debug("Getting bare transport graph")
        return _TransportGraph(lattice_id, True)


def _filter_node(node_obj: Node, session: Session, attr_keys: List[str]):
    output = {"node_id": node_obj.node_id}
    for key in attr_keys:
        output[key] = node_obj.get_value(key, session, refresh=False)
    return output


def _filter_node_list(node_list: List[Node], session: Session, attr_keys: List[str]):
    return list(map(lambda x: _filter_node(x, session, attr_keys), node_list))
