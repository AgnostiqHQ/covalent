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
Tests for the graph querying functions
"""


from unittest.mock import MagicMock

import pytest

from covalent_dispatcher._core.data_modules import graph


@pytest.mark.asyncio
async def test_get_incoming_edges(mocker):
    dispatch_id = "test_get_incoming_edges"
    node_id = 0

    mock_result_obj = MagicMock()
    mock_return_val = [{"source": 1, "target": 0, "attrs": {"param_type": "arg"}}]
    mock_result_obj.lattice.transport_graph.get_incoming_edges = MagicMock(
        return_value=mock_return_val
    )

    mocker.patch(
        "covalent_dispatcher._core.data_modules.graph.get_result_object",
        return_value=mock_result_obj,
    )

    assert mock_return_val == await graph.get_incoming_edges(dispatch_id, node_id)


@pytest.mark.asyncio
async def test_get_node_successors(mocker):
    dispatch_id = "test_get_node_successors"
    node_id = 0

    mock_result_obj = MagicMock()
    mock_return_val = {"node_id": 0, "status": "NEW_OBJECT"}
    mock_result_obj.lattice.transport_graph.get_successors = MagicMock(
        return_value=mock_return_val
    )
    mocker.patch(
        "covalent_dispatcher._core.data_modules.graph.get_result_object",
        return_value=mock_result_obj,
    )
    assert mock_return_val == await graph.get_node_successors(dispatch_id, node_id)


@pytest.mark.asyncio
async def test_get_node_links(mocker):
    dispatch_id = "test_get_node_links"

    mock_result_obj = MagicMock()

    mock_return_val = {"nodes": [0, 1], "links": [(1, 0, 0)]}
    mocker.patch("networkx.readwrite.node_link_data", return_value=mock_return_val)
    mocker.patch(
        "covalent_dispatcher._core.data_modules.graph.get_result_object",
        return_value=mock_result_obj,
    )

    assert mock_return_val == await graph.get_nodes_links(dispatch_id)


@pytest.mark.asyncio
async def test_get_nodes(mocker):
    dispatch_id = "test_get_nodes"
    mock_result_obj = MagicMock()

    g = MagicMock()
    mock_result_obj.lattice.transport_graph.get_internal_graph_copy = MagicMock(return_value=g)
    g.nodes = [1, 2, 3]
    mocker.patch(
        "covalent_dispatcher._core.data_modules.graph.get_result_object",
        return_value=mock_result_obj,
    )

    assert [1, 2, 3] == await graph.get_nodes(dispatch_id)
