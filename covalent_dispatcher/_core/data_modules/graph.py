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

"""
Utilities for querying the transport graph
"""


# Note: these query static information which should be amenable to caching

from typing import Dict, List

import networkx as nx

from ..._dal.result import get_result_object
from .utils import run_in_executor


def get_incoming_edges_sync(dispatch_id: str, node_id: int):
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


def get_node_successors_sync(
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


def get_nodes_links_sync(dispatch_id: str) -> dict:
    """Return the internal transport graph in NX node-link form"""

    # Need the whole NX graph here
    result_object = get_result_object(dispatch_id, False)
    g = result_object.lattice.transport_graph.get_internal_graph_copy()
    return nx.readwrite.node_link_data(g)


def get_nodes_sync(dispatch_id: str) -> List[int]:
    """Return a list of all node ids in the graph."""
    result_object = get_result_object(dispatch_id, False)
    g = result_object.lattice.transport_graph.get_internal_graph_copy()
    return list(g.nodes)


async def get_incoming_edges(dispatch_id: str, node_id: int):
    return await run_in_executor(get_incoming_edges_sync, dispatch_id, node_id)


async def get_node_successors(
    dispatch_id: str,
    node_id: int,
    attrs: List[str] = ["task_group_id"],
) -> List[Dict]:
    return await run_in_executor(get_node_successors_sync, dispatch_id, node_id, attrs)


async def get_nodes_links(dispatch_id: str) -> Dict:
    return await run_in_executor(get_nodes_links_sync, dispatch_id)


async def get_nodes(dispatch_id: str) -> List[int]:
    return await run_in_executor(get_nodes_sync, dispatch_id)
