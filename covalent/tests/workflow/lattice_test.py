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


"""Unit tests for lattice."""

import importlib
from pathlib import Path
from typing import Callable, List

import networkx as nx
import pytest

from covalent._results_manager.result import Result
from covalent._shared_files.config import get_config
from covalent._shared_files.defaults import (
    _DEFAULT_CONFIG,
    _DEFAULT_CONSTRAINT_VALUES,
    parameter_prefix,
)
from covalent._workflow.electron import electron
from covalent._workflow.lattice import Lattice, lattice
from covalent._workflow.transport import _TransportGraph
from covalent.executor import LocalExecutor


@electron
def sample_task(x):
    """Sample task."""

    return x**2


def sample_workflow(a, b):
    """Sample workflow."""

    c = sample_task(a)
    d = sample_task(b)
    return c, d


@pytest.fixture
def test_task_function():
    """Test function."""

    return sample_task


@pytest.fixture
def test_workflow_function():
    return sample_workflow


@pytest.fixture
def test_lattice():
    return lattice(sample_workflow)


@pytest.fixture
def task_arg_name():
    return "x"


@pytest.fixture
def sample_values():
    return [1, 2]


@pytest.fixture
def init_mock(mocker):
    return mocker.patch("covalent._workflow.lattice.Lattice.__init__", return_value=None)


def test_lattice_init(mocker):
    sample_import_string = """\
import pytest
import platform as pf
# import covalent as ct\
"""
    sample_imports = set()
    sample_imports.add("ct")

    get_imports_mock = mocker.patch(
        "covalent._workflow.lattice.get_imports",
        return_value=(sample_import_string, sample_imports),
    )

    serialized_function_str = """\
@ct.lattice
def workflow(x):
    return func(x)\
"""
    get_ser_func_string_mock = mocker.patch(
        "covalent._workflow.lattice.get_serialized_function_str",
        return_value=serialized_function_str,
    )

    test_lattice = Lattice(sample_workflow)

    get_imports_mock.assert_called_once_with(sample_workflow)
    get_ser_func_string_mock.assert_called_once_with(sample_workflow)

    # Also test an empty transport graph can be passed
    test_lattice_alt = Lattice(sample_workflow, _TransportGraph())

    assert test_lattice.workflow_function == sample_workflow
    assert test_lattice.workflow_function_string == serialized_function_str
    assert test_lattice.__name__ == sample_workflow.__name__
    assert test_lattice.lattice_imports == sample_import_string
    test_lattice.cova_imports.update({"electron"})
    assert test_lattice.cova_imports == sample_imports


def test_set_metadata(mocker, init_mock):
    test_lattice = Lattice(sample_workflow)
    test_lattice.metadata = {}
    init_mock.assert_called_once_with(sample_workflow)

    test_lattice.set_metadata("test_key", "test_value")

    assert test_lattice.metadata["test_key"] == "test_value"


def test_get_metadata(mocker, init_mock):
    test_lattice = Lattice(sample_workflow)
    test_lattice.metadata = {"test_key": "test_value"}
    init_mock.assert_called_once_with(sample_workflow)

    value = test_lattice.get_metadata("test_key")
    assert value == "test_value"

    bad_value = test_lattice.get_metadata("missing_entry")
    assert bad_value is None


# TODO: Complete and improve this test
def test_lattice_build_graph(task_arg_name: str, sample_values: List):
    """Test that the graph is built correctly."""

    @lattice
    def reference_lattice(a, b):
        """Sample workflow."""

        c = sample_task(a)
        d = sample_task(b)
        return c, d

    new_graph = _TransportGraph()
    executor = LocalExecutor()

    # Start adding node and edge to the graph
    for val in sample_values:
        node_id_1 = new_graph.add_node(
            name=sample_task.__name__,
            function=sample_task,
            metadata={"executor": executor},
            key=0,
            task_arg_name=val,
        )

        node_id_2 = new_graph.add_node(
            name=parameter_prefix + str(val),
            function=None,
            metadata={"executor": executor},
            key=1,
            task_arg_name=val,
        )

        new_graph.add_edge(node_id_2, node_id_1, task_arg_name)

    # Building the reference graph
    reference_lattice.build_graph(sample_values[0], sample_values[1])

    def dict_match(dict1, dict2) -> bool:
        """Check if two dictionaries are equal, barring 'complicated' objects."""

        for key in dict1:
            if key not in dict2:
                return False
            if key == "executor":
                if not isinstance(dict1[key], type(dict2[key])):
                    return False
            elif dict1[key] != dict2[key]:
                return False
        for key in dict2:
            if key not in dict1:
                return False
        return True

    def are_matching_nodes(node_1, node_2):
        """Check if two nodes are the same."""

        attr_to_check = ["name", "metadata"]
        node_match = [
            dict_match(node_1[attr], node_2[attr])
            if attr == "metadata"
            else node_1[attr] == node_2[attr]
            for attr in attr_to_check
        ]
        return all(node_match)

    # Testing the graph
    graph_to_test = reference_lattice.transport_graph.get_internal_graph_copy()
    sample_graph = new_graph.get_internal_graph_copy()

    # Check similarity without considering node attributes
    assert nx.graph_edit_distance(graph_to_test, sample_graph) == 0

    # Check similarity considering node attributes
    assert nx.graph_edit_distance(graph_to_test, sample_graph, node_match=are_matching_nodes) == 0


def test_draw(mocker, init_mock):
    test_lattice = Lattice(sample_workflow)

    build_graph_mock = mocker.patch(
        "covalent._workflow.lattice.Lattice.build_graph", return_value=None
    )
    webhook_call_mock = mocker.patch(
        "covalent._workflow.lattice.result_webhook.send_draw_request", return_value=None
    )

    test_args = [1, 2, 3]
    test_kwargs = {"x": 1, "y": 2, "z": 3}
    test_lattice.draw(*test_args, **test_kwargs)

    build_graph_mock.assert_called_once_with(*test_args, **test_kwargs)
    webhook_call_mock.assert_called_once_with(test_lattice)


def test_lattice_call(
    test_workflow_function: Callable, test_task_function: Callable, sample_values: List
):
    """Test that lattice can be called as a normal function"""

    output_1, output_2 = test_workflow_function(sample_values[0], sample_values[1])

    assert output_1 == test_task_function(sample_values[0])
    assert output_2 == test_task_function(sample_values[1])


@pytest.mark.skip(reason="not yet implemented")
def test_lattice_check_constraint_specific_sum(test_workflow_function: Callable):
    """Test that lattice can check constraint specific sum."""

    # TODO: This is getting really hard to test because first, we don't
    # have an interface to the electron to change the `budget` and `time_limit` constraints
    # and second, this is an old function which is only here for so that if needed, we can
    # support validating that electron constraints don't exceed lattice's constraints.

    # What we can do is either modify how this function inputs things and then test it.

    # graph = test_lattice.transport_graph.get_internal_graph_copy()
    # data = nx.readwrite.node_link_data(graph)

    # for constraint in ["budget", "time_limit"]:

    pass


@pytest.mark.skip(reason="not yet implemented")
def test_lattice_check_consumable():
    """Test that lattice can check consumable constraint limits."""

    # TODO: Same as above.
    pass


def test_lattice_decorator(mocker, monkeypatch):
    mock_config_call = mocker.patch(
        "covalent._workflow.lattice.get_config", return_value="results"
    )
    monkeypatch.setattr(
        "covalent._shared_files.defaults._DEFAULT_CONSTRAINT_VALUES", {"executor": "local"}
    )

    # Test lattice can be called using no arguments to return a decorator function
    empty_lattice = lattice()
    assert callable(empty_lattice)
    assert empty_lattice.__name__ == "decorator_lattice"

    # Use 1: delayed application of the decorator
    test_lattice_1 = empty_lattice(sample_workflow)
    assert callable(test_lattice_1)
    assert isinstance(test_lattice_1, Lattice)
    # A few functional assertions
    assert test_lattice_1.__name__ == sample_workflow.__name__
    assert test_lattice_1(1, 2) == sample_workflow(1, 2)

    # Use 2: direct application of the decorator
    test_lattice_2 = lattice(sample_workflow)
    assert callable(test_lattice_2)
    assert isinstance(test_lattice_2, Lattice)

    # Use 3: wrap a function
    @lattice
    def test_workflow(x):
        return sample_task(x)

    assert isinstance(test_workflow, Lattice)
    assert test_workflow.__name__ == "test_workflow"

    # Test the constraints are applied
    assert isinstance(test_workflow.metadata["executor"], LocalExecutor)
    assert test_workflow.metadata["results_dir"] == str(Path("results").expanduser().resolve())
    assert test_workflow.metadata["notify"] == []

    # Finally test deprecated variables are properly forwarded
    test_lattice_3 = lattice(sample_workflow, backend="local")
    assert isinstance(test_lattice_3.metadata["executor"], LocalExecutor)
