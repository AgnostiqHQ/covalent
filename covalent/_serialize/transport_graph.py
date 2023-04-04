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

"""Functions to convert tg -> TransportGraphSchema"""

import os
from pathlib import Path
from typing import List

import networkx as nx

from .._shared_files.schemas.edge import EdgeMetadata, EdgeSchema
from .._shared_files.schemas.electron import ElectronSchema
from .._shared_files.schemas.transport_graph import TransportGraphSchema
from .._workflow.transport import _TransportGraph
from .electron import deserialize_node, serialize_node


def serialize_edge(source: int, target: int, attrs: dict) -> EdgeSchema:
    meta = EdgeMetadata(
        edge_name=attrs["edge_name"],
        param_type=attrs.get("param_type"),
        arg_index=attrs.get("arg_index"),
    )
    return EdgeSchema(source=source, target=target, metadata=meta)


def deserialize_edge(e: EdgeSchema) -> dict:
    return {
        "source": e.source,
        "target": e.target,
        "attrs": e.metadata.dict(),
    }


def _serialize_nodes(g: nx.MultiDiGraph, storage_path: str) -> List[ElectronSchema]:
    results = []
    base_path = Path(storage_path)
    for i in g.nodes:
        node_storage_path = base_path / f"node_{i}"
        os.mkdir(node_storage_path)
        results.append(serialize_node(i, g.nodes[i], node_storage_path))
    return results


def _serialize_edges(g: nx.MultiDiGraph) -> List[EdgeSchema]:
    results = []
    for edge in g.edges:
        source, target, key = edge
        results.append(serialize_edge(source, target, g.edges[edge]))
    return results


def serialize_transport_graph(tg, storage_path: str) -> TransportGraphSchema:
    g = tg.get_internal_graph_copy()
    return TransportGraphSchema(
        nodes=_serialize_nodes(g, storage_path),
        links=_serialize_edges(g),
    )


def deserialize_transport_graph(t: TransportGraphSchema) -> _TransportGraph:
    tg = _TransportGraph()
    g = tg._graph
    nodes = [deserialize_node(n) for n in t.nodes]
    edges = [deserialize_edge(e) for e in t.links]
    for node in nodes:
        node_id = node["id"]
        attrs = node["attrs"]
        g.add_node(node_id, **attrs)
    for edge in edges:
        x = edge["source"]
        y = edge["target"]
        g.add_edge(x, y, **edge["attrs"])

    return tg
