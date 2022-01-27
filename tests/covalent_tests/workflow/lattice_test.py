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

import networkx as nx
import pytest

from typing import Callable, List

from covalent._shared_files.defaults import default_constraints_dict, parameter_prefix
from covalent._workflow.electron import electron
from covalent._workflow.lattice import Lattice, lattice
from covalent._workflow.transport import _TransportGraph


@electron
def sample_task(x):
    """Sample task."""

    return x ** 2


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


def test_lattice_build_graph(test_lattice: Lattice, task_arg_name: str, sample_values: List):
    """Test that the graph is built correctly."""

    new_graph = _TransportGraph()

    # Start adding node and edge to the graph
    for val in sample_values:
        node_id_1 = new_graph.add_node(
            sample_task.__name__, {task_arg_name: val}, sample_task, {"backend": "local"}
        )

        node_id_2 = new_graph.add_node(
            parameter_prefix + str(val),
            {task_arg_name: val},
            None,
            default_constraints_dict.copy(),
        )

        new_graph.add_edge(node_id_2, node_id_1, task_arg_name)

    # Building the graph
    test_lattice.build_graph(sample_values[0], sample_values[1])

    def are_matching_nodes(node_1, node_2):
        """Check if two nodes are the same."""

        attr_to_check = ["name", "kwargs", "metadata"]
        return all(node_1[attr] == node_2[attr] for attr in attr_to_check)

    # Testing the graph
    graph_to_test = test_lattice.transport_graph.get_internal_graph_copy()
    sample_graph = new_graph.get_internal_graph_copy()

    # Check similarity without considering node attributes
    assert nx.graph_edit_distance(graph_to_test, sample_graph) == 0
    # Check similarity considering node attributes
    assert nx.graph_edit_distance(graph_to_test, sample_graph, node_match=are_matching_nodes) == 0


def test_lattice_call(test_workflow_function: Callable, test_task_function: Callable, sample_values: List):
    """Test that lattice can be called as a normal function"""

    output_1, output_2 = test_workflow_function(sample_values[0], sample_values[1])

    assert output_1 == test_task_function(sample_values[0])
    assert output_2 == test_task_function(sample_values[1])


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


def test_lattice_check_consumable():
    """Test that lattice can check consumable constraint limits."""

    # TODO: Same as above.
    pass

