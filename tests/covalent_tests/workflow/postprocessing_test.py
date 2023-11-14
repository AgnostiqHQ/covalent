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

"""Unit tests for the preprocessing module."""

from unittest.mock import MagicMock, Mock

import pytest
from mock import call

import covalent as ct
from covalent._shared_files.defaults import postprocess_prefix
from covalent._workflow.electron import Electron
from covalent._workflow.postprocessing import Postprocessor
from covalent.executor import LocalExecutor


@pytest.fixture
def postprocessor():
    """Get postprocessor object."""

    le = LocalExecutor()

    @ct.electron(executor="local")
    def task_1(x):
        return x

    @ct.electron(executor="local")
    def task_2(x):
        return [x * 2]

    @ct.lattice(executor=le, workflow_executor="dask")
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
    mock_lattice.inputs = MagicMock()
    mock_lattice.inputs.get_deserialized = MagicMock(
        return_value={"args": (mock_arg,), "kwargs": {"mock_key": mock_kwarg}}
    )
    mock_lattice.workflow_function = mock_workflow

    pp = Postprocessor(mock_lattice)
    res = pp._postprocess(["mock_output_1", "mock_output_2"])

    assert mock_lattice.electron_outputs == [["mock_output_1", "mock_output_2"]]
    mock_workflow.get_deserialized().assert_called_once_with(mock_arg, mock_key=mock_kwarg)

    assert res == "mock_result"


@pytest.mark.parametrize(
    "retval, node_ids",
    [
        (Electron(function=lambda x: x, node_id=1), {1}),
        (
            [Electron(function=lambda x: x, node_id=1), Electron(function=lambda x: x, node_id=2)],
            {1, 2},
        ),
        (
            {
                "a": Electron(function=lambda x: x, node_id=1),
                "b": Electron(function=lambda x: x, node_id=2),
            },
            {1, 2},
        ),
        ("unsupported", []),
    ],
)
def test_get_node_ids_from_retval(postprocessor, retval, node_ids):
    """Test get_node_ids_from_retval method."""
    assert postprocessor._get_node_ids_from_retval(retval) == node_ids


def test_get_electron_metadata(postprocessor):
    """Test method that retrieves the postprocessing electron metadata."""
    metadata_copy = postprocessor.lattice.metadata.copy()
    metadata_copy["executor"] = metadata_copy.pop("workflow_executor")
    metadata_copy["executor_data"] = metadata_copy.pop("workflow_executor_data")
    assert postprocessor._get_electron_metadata() == metadata_copy


def test_add_exhaustive_postprocess_node(postprocessor):
    """Test method that adds exhaustive postprocess node."""
    node_num = len(postprocessor.lattice.transport_graph._graph.nodes)
    postprocessor.add_exhaustive_postprocess_node({})
    assert len(postprocessor.lattice.transport_graph._graph.nodes) == node_num + 1
    assert (
        postprocessor.lattice.transport_graph._graph.nodes(data=True)[0]["name"]
        == postprocess_prefix
    )


def test_add_reconstruct_postprocess_node(postprocessor, mocker):
    """Test method that adds eager postprocess node."""

    def test_func(x):
        return x

    get_node_ids_from_retval_mock = mocker.patch(
        "covalent._workflow.postprocessing.Postprocessor._get_node_ids_from_retval"
    )
    get_electron_metadata_mock = mocker.patch(
        "covalent._workflow.postprocessing.Postprocessor._get_electron_metadata"
    )

    mock_electron = Electron(function=test_func, node_id=0)
    mock_bound_electrons = {0: mock_electron}
    postprocessor.add_reconstruct_postprocess_node(mock_electron, mock_bound_electrons)
    get_electron_metadata_mock.assert_called_once_with()
    assert get_node_ids_from_retval_mock.mock_calls == [
        call(mock_electron),
        call().__iter__(),
        call().__contains__(0),
    ]


def test_postprocess_recursively(postprocessor, mocker):
    """Test postprocess_recursively method."""

    def test_func(x):
        return x

    mock_electron_0 = Electron(function=test_func, node_id=0)
    res = postprocessor._postprocess_recursively(mock_electron_0, **{"node:0": "mock-output-0"})
    assert res == "mock-output-0"

    mock_electron_1 = Electron(function=test_func, node_id=1)
    res = postprocessor._postprocess_recursively(
        [mock_electron_0, mock_electron_1],
        **{"node:0": "mock-output-0", "node:1": "mock-output-1"},
    )
    assert res == ["mock-output-0", "mock-output-1"]

    res = postprocessor._postprocess_recursively(
        {mock_electron_0, mock_electron_1},
        **{"node:0": "mock-output-0", "node:1": "mock-output-1"},
    )
    assert res == {"mock-output-0", "mock-output-1"}

    res = postprocessor._postprocess_recursively(
        (mock_electron_0, mock_electron_1),
        **{"node:0": "mock-output-0", "node:1": "mock-output-1"},
    )
    assert res == ("mock-output-0", "mock-output-1")

    res = postprocessor._postprocess_recursively(
        {"0": mock_electron_0, "1": mock_electron_1},
        **{"node:0": "mock-output-0", "node:1": "mock-output-1"},
    )
    assert res == {"0": "mock-output-0", "1": "mock-output-1"}

    res = postprocessor._postprocess_recursively(
        "mock",
        **{"node:0": "mock-output-0", "node:1": "mock-output-1"},
    )
    assert res == "mock"
