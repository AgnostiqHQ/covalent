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

"""Unit tests for the preprocessing module."""

from unittest.mock import MagicMock, Mock

import pytest

import covalent as ct
from covalent._shared_files.defaults import postprocess_prefix
from covalent._workflow.electron import Electron
from covalent._workflow.postprocessing import Postprocessor


@pytest.fixture
def postprocessor():
    """Get postprocessor object."""

    @ct.electron(executor="local")
    def task_1(x):
        return x

    @ct.electron(executor="local")
    def task_2(x):
        return [x * 2]

    @ct.lattice(executor="local")
    def workflow(x):
        res_1 = task_1(x)
        res_2 = task_2(x)
        return [res_1] + res_2

    return Postprocessor(workflow)


def test_postprocessor_init(postprocessor):
    """Test postprocessor initialization."""
    assert postprocessor.lattice(1) == [1, 2]


@pytest.mark.parametrize(
    "node_id, node_name, postprocessable",
    [
        (0, ":parameter:1", False),
        (1, "task_2", True),
        (2, ":sublattice:task_2", True),
        (3, ":postprocess:", False),
    ],
)
def test_is_postprocessable_node(mocker, postprocessor, node_id, node_name, postprocessable):
    """Test is_postprocessable_node method."""
    postprocessor.lattice.build_graph(1)
    tg = postprocessor.lattice.transport_graph

    mocker.patch(
        "covalent._workflow.postprocessing._TransportGraph.get_node_value", return_value=node_name
    )
    assert postprocessor._is_postprocessable_node(tg, node_id) == postprocessable


def test_filter_electrons(postprocessor):
    """Test filter_electrons method."""
    postprocessor.lattice.build_graph(1)
    tg = postprocessor.lattice.transport_graph
    mock_bound_electrons = {i: f"mock_electron_{i}" for i in range(12)}
    assert postprocessor._filter_electrons(tg, mock_bound_electrons) == [
        f"mock_electron_{i}" for i in [0, 2, 4]
    ]


def test_postprocess():
    """Test the postprocess method."""
    mock_lattice = MagicMock()
    mock_arg = Mock()
    mock_kwarg = Mock()
    mock_workflow = Mock()
    mock_workflow.get_deserialized.__call__().return_value = "mock_result"
    mock_lattice.args.__iter__.return_value = [mock_arg]
    mock_lattice.kwargs = {"mock_key": mock_kwarg}
    mock_lattice.workflow_function = mock_workflow

    pp = Postprocessor(mock_lattice)
    res = pp._postprocess(["mock_output_1", "mock_output_2"])

    assert mock_lattice.electron_outputs == [["mock_output_1", "mock_output_2"]]

    mock_arg.get_deserialized.assert_called_once_with()
    mock_kwarg.get_deserialized.assert_called_once_with()
    mock_workflow.get_deserialized().assert_called_once_with(
        mock_arg.get_deserialized(), mock_key=mock_kwarg.get_deserialized()
    )

    assert res == "mock_result"


@pytest.mark.parametrize(
    "retval, node_ids",
    [
        (Electron(function=lambda x: x, node_id=1), [1]),
        (
            [Electron(function=lambda x: x, node_id=1), Electron(function=lambda x: x, node_id=2)],
            [1, 2],
        ),
        (
            {
                "a": Electron(function=lambda x: x, node_id=1),
                "b": Electron(function=lambda x: x, node_id=2),
            },
            [1, 2],
        ),
        ("unsupported", []),
    ],
)
def test_get_node_ids_from_retval(postprocessor, retval, node_ids):
    """Test get_node_ids_from_retval method."""
    assert postprocessor._get_node_ids_from_retval(retval) == node_ids


def test_get_electron_metadata(postprocessor):
    """Test method that retrieves the postprocessing electron metadata."""
    assert postprocessor._get_electron_metadata() == {
        "executor": None,
        "deps": {},
        "call_before": [],
        "call_after": [],
        "workflow_executor": "local",
        "executor_data": {},
        "workflow_executor_data": {},
    } or {
        "executor": None,
        "deps": {},
        "call_before": [],
        "call_after": [],
        "workflow_executor": "dask",
        "executor_data": {},
        "workflow_executor_data": {},
    }


def test_add_exhaustive_postprocess_node(postprocessor):
    """Test method that adds exhaustive postprocess node."""
    node_num = len(postprocessor.lattice.transport_graph._graph.nodes)
    postprocessor.add_exhaustive_postprocess_node({})
    assert len(postprocessor.lattice.transport_graph._graph.nodes) == node_num + 1
    assert (
        postprocessor.lattice.transport_graph._graph.nodes(data=True)[0]["name"]
        == postprocess_prefix
    )
