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

"""
Utilities for querying the transport graph
"""


# Note: these query static information which should be amenable to caching

from typing import Dict, List

import networkx as nx

from ..._dal.result import get_result_object


def get_incoming_edges(dispatch_id: str, node_id: int):
    """Query in-edges of a node.

    Returns:
        List[Edge], where

        Edge is a dictionary with structure
            source: int,
            target: int,
            attrs: dict
    """

    result_object = get_result_object(dispatch_id)
    return result_object.lattice.transport_graph.get_incoming_edges(node_id)


def get_node_successors(
    dispatch_id: str,
    node_id: int,
    attrs: List[str],
) -> List[Dict]:
    """Get child nodes with multiplicity.

    Parameters:
        node_id: id of node
        attr_keys: list of node attributes to return, such as task_group_id

    Returns:
        List[Dict], where each dictionary is of the form
        {"node_id": node_id, attr_key_1: node_attr[attr_key_1], ...}

    """

    result_object = get_result_object(dispatch_id)
    return result_object.lattice.transport_graph.get_successors(node_id, attrs)


def get_graph_nodes_links(dispatch_id: str) -> dict:
    """Return the internal transport graph in NX node-link form"""

    # Need the whole NX graph here
    result_object = get_result_object(dispatch_id, False)
    g = result_object.lattice.transport_graph.get_internal_graph_copy()
    return nx.readwrite.node_link_data(g)


def get_nodes(dispatch_id: str) -> List[int]:
    # Read the whole NX graph
    result_object = get_result_object(dispatch_id, False)
    g = result_object.lattice.transport_graph.get_internal_graph_copy()
    return list(g.nodes)
