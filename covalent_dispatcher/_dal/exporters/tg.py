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


"""Functions to transform TransportGraph -> TransportGraphSchema"""

from typing import List

from covalent._shared_files import logger
from covalent._shared_files.schemas.edge import EdgeMetadata, EdgeSchema
from covalent._shared_files.schemas.electron import ElectronSchema
from covalent._shared_files.schemas.transport_graph import TransportGraphSchema

from ..tg import _TransportGraph
from .electron import export_electron

app_log = logger.app_log


# Transport Graphs are assumed to be full, with a complete internal NX graph
def _export_nodes(tg: _TransportGraph) -> List[ElectronSchema]:
    g = tg.get_internal_graph_copy()
    internal_nodes = tg.get_nodes(list(g.nodes), None)
    export_nodes = []
    for e in internal_nodes:
        export_nodes.append(export_electron(e))

    return export_nodes


def _export_edges(tg: _TransportGraph) -> List[EdgeSchema]:
    edge_list = []
    g = tg.get_internal_graph_copy()
    for edge in g.edges:
        source, target, key = edge
        edge_metadata = EdgeMetadata(**g.edges[edge])
        edge_list.append(EdgeSchema(source=source, target=target, metadata=edge_metadata))

    return edge_list


def export_transport_graph(tg: _TransportGraph) -> TransportGraphSchema:
    node_list = _export_nodes(tg)
    edge_list = _export_edges(tg)
    app_log.debug(f"Exporting {len(node_list)} nodes and {len(edge_list)} edges")
    return TransportGraphSchema(nodes=node_list, links=edge_list)
