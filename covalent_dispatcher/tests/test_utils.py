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

"""Unit tests for utils module"""

from copy import deepcopy
from io import BytesIO
from unittest import mock

import cloudpickle as pickle
import pytest
import requests
import requests_mock
from app.core.dispatch_workflow import init_result_pre_dispatch
from app.core.utils import (
    are_tasks_running,
    generate_task_result,
    get_parent_id_and_task_id,
    get_task_inputs,
    get_task_order,
    is_empty,
    is_sublattice,
    is_sublattice_dispatch_id,
    send_cancel_task_to_runner,
    send_task_list_to_runner,
    send_task_update_to_dispatcher,
)

import covalent as ct
from covalent._results_manager.result import Result


@pytest.fixture
def mock_tasks_queue():
    """Construct mock tasks queue."""

    from multiprocessing import Queue as MPQ

    return MPQ()


@pytest.fixture
def mock_task():
    """Construct a mock task object"""
    task_object = {
        "task_id": "mock_task_id",
        "start_time": "0.00",
        "end_time": "0.01",
        "status": "NEW",
    }

    return task_object


@pytest.fixture
def mock_task_list(mock_result_uninitialized):
    result_obj = deepcopy(mock_result_uninitialized)

    init_result_pre_dispatch(result_obj)

    tasks_list = [
        {
            "task_id": 0,
            "func": "add",
            "args": [2, 3],
            "kwargs": {},
            "results_dir": result_obj.results_dir,
        },
        {
            "task_id": 2,
            "func": "square",
            "args": [2],
            "kwargs": {},
            "results_dir": result_obj.results_dir,
        },
    ]
    return tasks_list


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

    return Result(lattice=lattice, results_dir="", dispatch_id="mock_dispatch_id")


@pytest.fixture
def mock_result_initialized(mock_result_uninitialized):
    """Initialize mock result object."""

    result_obj = deepcopy(mock_result_uninitialized)

    init_result_pre_dispatch(result_obj)
    return result_obj


def test_is_empty(mock_tasks_queue):
    """Test that the MPQ contains only one element at any time."""

    with pytest.raises(Exception):
        mock_tasks_queue.get(timeout=1)
    assert is_empty(mock_tasks_queue) is True


def test_preprocess_transport_graph():
    """Test that the execution status of the task nodes in the transport graph are properly initialized."""

    pass


def test_post_process():
    """Test that lattice is post-processed correctly after execution of the nodes in the transport graph"""

    pass


def test_get_task_inputs(mock_result_initialized):
    """
    Test that inputs for a given task execution are returned as dictionaries containing args, kwargs,
    and any parent node execution results if present."""

    node_names = mock.Mock(
        "node_names",
        return_value=[
            ":electron_list:add",
            "1",
            "2",
            ":electron_dict_prefix:square",
            "3",
            "multiply",
        ],
    )
    node_keys = [0, 1]
    result_obj = mock_result_initialized

    for node_key in node_keys:
        for node_name in node_names.return_value:
            if node_name.startswith(":electron_list:") and node_key == 0:
                assert get_task_inputs(node_key, node_name, result_obj) == {
                    "args": [],
                    "kwargs": {"x": [None, None]},
                }
            elif node_name.startswith(":electron_list:") and node_key == 1:
                assert get_task_inputs(node_key, node_name, result_obj) == {
                    "args": [],
                    "kwargs": {"x": []},
                }
            elif node_name.startswith(":electron_dict_prefix:") and node_key == 0:
                assert get_task_inputs(node_key, node_name, result_obj) == {
                    "args": [None, None],
                    "kwargs": {},
                }
            elif node_name.startswith(":electron_dict_prefix:") and node_key == 1:
                assert get_task_inputs(node_key, node_name, result_obj) == {
                    "args": [],
                    "kwargs": {},
                }
            else:
                if node_key == 0:
                    assert get_task_inputs(node_key, node_name, result_obj) == {
                        "args": [None, None],
                        "kwargs": {},
                    }
                elif node_key == 1:
                    assert get_task_inputs(node_key, node_name, result_obj) == {
                        "args": [],
                        "kwargs": {},
                    }


def test_is_sublattice():
    """Test sublattice check on a transport graph node"""
    mock_node_names = mock.Mock("mock_node_names", return_value=["task1", "task2", "task3"])
    sublattice_prefix = ":sublattice:"
    for node_name in mock_node_names.return_value:
        assert not is_sublattice(node_name)
        sublattice_node_name = sublattice_prefix + node_name
        assert is_sublattice(sublattice_node_name)


def test_are_tasks_running(mock_result_uninitialized):
    """Test to check if node tasks are running. Asserts true if the status of any task is running or if the task is a
    new object."""
    mock_result_initialized = init_result_pre_dispatch(mock_result_uninitialized)
    assert are_tasks_running(mock_result_initialized) and are_tasks_running(
        mock_result_uninitialized
    )


def test_get_task_order(mock_result_uninitialized):
    """Test to check the correct order for executing the task nodes in a transport graph"""
    sorted_nodes = [[1, 2, 4], [0, 3], [5]]
    mock_result_initialized = init_result_pre_dispatch(mock_result_uninitialized)
    assert get_task_order(mock_result_initialized) == sorted_nodes


def test_send_task_list_to_runner(mocker, mock_result_uninitialized, mock_task_list):
    """Test for sending task list to runner."""
    dispatch_id = mock_result_uninitialized.dispatch_id
    task_list = mock_task_list
    mock_url_endpoint = f"http://localhost:8003/api/v0/workflow/{dispatch_id}/tasks"
    session = requests.Session()
    adapter = requests_mock.Adapter()
    session.mount("http://localhost", adapter)
    adapter.register_uri("POST", mock_url_endpoint)
    response = session.post(mock_url_endpoint, files={"tasks": BytesIO(pickle.dumps(task_list))})
    assert response.status_code == 200
    mock_send_list_to_runner = mocker.patch(
        "app.core.utils.send_task_list_to_runner", return_value=[]
    )
    assert mock_send_list_to_runner(dispatch_id, task_list) == []
    mock_send_list_to_runner.assert_called_with(dispatch_id, task_list)


def test_send_result_object_to_result_service():
    """Test for sending result object to result microservice."""
    pass


def test_send_task_update_to_result_service():
    """Test for sending task update to result service."""
    pass


def test_send_task_update_to_ui():
    """Test for sending task update to ui backend microservice."""
    pass


def test_get_result_object_from_result_service():
    """Test result object pickling from the result microservice."""
    pass


def test_update_result_and_ui():
    """Test that the UI is updated and the result is written to the database."""

    pass


def test_send_cancel_task_to_runner(mock_result_uninitialized):
    """Test that the task to be cancelled by the runner returns a non-empty tuple containing the cancelled dispatch
    id and task id."""

    mock_dispatch_id = mock_result_uninitialized.dispatch_id
    mock_task_id = 1
    mock_cancel_url_endpoint = (
        f"http://localhost:8003/api/v0/workflow/{mock_dispatch_id}/task/{mock_task_id}/cancel"
    )

    session = requests.Session()
    adapter = requests_mock.Adapter()
    session.mount("http://localhost", adapter)
    adapter.register_uri("DELETE", mock_cancel_url_endpoint)
    response = session.delete(mock_cancel_url_endpoint)
    assert response.status_code == 200


def test_is_sublattice_dispatch_id(mock_result_uninitialized):
    """Test for sublattice dispatch id"""
    mock_dispatch_id = mock_result_uninitialized.dispatch_id
    assert not is_sublattice_dispatch_id(mock_dispatch_id)
    mock_dispatch_id += ":"
    assert is_sublattice_dispatch_id(mock_dispatch_id)


def test_send_task_update_to_dispatcher(mock_result_initialized):
    """Test for sending task update to dispatcher"""
    mock_dispatch_id = mock_result_initialized.dispatch_id
    mock_dispatch_url_endpoint = f"http://localhost:8002/api/v0/workflow/{mock_dispatch_id}"
    session = requests.Session()
    adapter = requests_mock.Adapter()
    session.mount("http://localhost", adapter)
    adapter.register_uri("PUT", mock_dispatch_url_endpoint)
    response = session.put(
        mock_dispatch_url_endpoint,
        files={"task_execution_results": pickle.dumps(mock_result_initialized.result)},
    )
    response.raise_for_status()
    assert response.status_code == 200


def test_generate_task_result(mock_task):
    """Test for generating the result of a task"""

    mock_task_object = mock_task
    mock_return_value = {
        "task_id": mock_task_object["task_id"],
        "start_time": mock_task_object["start_time"],
        "end_time": mock_task_object["end_time"],
        "status": mock_task_object["status"],
        "output": None,
        "error": None,
        "stdout": None,
        "stderr": None,
        "info": None,
    }
    mock_task_result = mock.Mock("task result", return_value=mock_return_value)
    assert (
        generate_task_result(
            mock_task_object["task_id"],
            mock_task_object["start_time"],
            mock_task_object["end_time"],
            mock_task_object["status"],
            None,
            None,
            None,
            None,
            None,
        )
        == mock_task_result.return_value
    )


def test_get_parent_id_and_task_id(mock_result_uninitialized):
    mock_dispatch_id = mock_result_uninitialized.dispatch_id
    assert get_parent_id_and_task_id(mock_dispatch_id) == (False, False)
