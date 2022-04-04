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

"""Unit tests for dispatch workflow."""

from copy import deepcopy

import pytest
from app.core.dispatch_workflow import init_result_pre_dispatch, is_runnable_task

import covalent as ct
from covalent._results_manager.result import Result
from covalent._workflow.transport import _TransportGraph


@pytest.fixture
def mock_result_uninitialized():
    """Construct mock result object."""

    @ct.electron
    def add(x, y):
        return x + y

    @ct.electron
    def multiply(x, y):
        return x * y

    @ct.electron
    def square(x):
        return x**2

    @ct.lattice
    def workflow(x, y, z):

        a = add(x, y)
        b = square(z)
        final = multiply(a, b)
        return final

    lattice = deepcopy(workflow)
    lattice.build_graph(x=1, y=2, z=3)
    lattice.transport_graph = lattice.transport_graph.serialize()

    return Result(lattice=lattice, results_dir="", dispatch_id="mock_dispatch_id")


@pytest.fixture
def mock_result_initialized(mock_result_uninitialized):
    """Construct mock result object."""

    result_obj = deepcopy(mock_result_uninitialized)

    init_result_pre_dispatch(result_obj)
    return result_obj


@pytest.fixture
def mock_tasks_queue():
    """Construct mock tasks queue."""

    from multiprocessing import Queue as MPQ

    return MPQ()


def test_dispatch_workflow_func(mocker, mock_result_initialized, mock_tasks_queue):
    """Test that the dispatch workflow function calls the appropriate method depending on the result object status."""

    mock_submit_workflow = mocker.patch("app.core.dispatch_workflow.submit_workflow")

    assert mock_result_initialized.status == Result.NEW_OBJ


def test_dispatch_runnable_tasks():
    pass


def test_start_dispatch():
    pass


def test_get_runnable_tasks():
    pass


def test_init_result_pre_dispatch(mocker, mock_result_uninitialized):
    """Test the result object initialization method."""

    mock_initialize_nodes = mocker.patch(
        "covalent._results_manager.result.Result._initialize_nodes"
    )

    assert isinstance(mock_result_uninitialized.lattice.transport_graph, bytes)

    post_init_result_obj = init_result_pre_dispatch(mock_result_uninitialized)
    assert isinstance(post_init_result_obj.lattice.transport_graph, _TransportGraph)

    mock_initialize_nodes.assert_called_once_with()


def test_run_tasks():
    pass


@pytest.mark.parametrize(
    "node_0_status,node_3_status,expected_runnable_status",
    [
        (Result.RUNNING, Result.RUNNING, False),
        (Result.COMPLETED, Result.RUNNING, False),
        (Result.FAILED, Result.RUNNING, False),
        (Result.COMPLETED, Result.COMPLETED, True),
    ],
)
def test_is_runnable_task(
    mock_result_initialized, node_0_status, node_3_status, expected_runnable_status
):
    """Test function that returns status of whether a task is runnable."""

    result_obj = mock_result_initialized
    result_obj.lattice.transport_graph.set_node_value(0, "status", node_0_status)
    result_obj.lattice.transport_graph.set_node_value(3, "status", node_3_status)

    assert is_runnable_task(task_id=5, result_obj=result_obj) == expected_runnable_status
