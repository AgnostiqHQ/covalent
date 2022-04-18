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

"""Unit tests for updating workflows."""

from copy import deepcopy
from datetime import datetime
from multiprocessing import Queue as MPQ

import pytest
from app.core.dispatch_workflow import init_result_pre_dispatch
from app.core.update_workflow import (
    update_completed_tasks,
    update_completed_workflow,
    update_workflow_endtime,
    update_workflow_results,
)

import covalent as ct
from covalent._results_manager import Result


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
def mock_tasks_queue():
    """Construct mock tasks queue."""

    from multiprocessing import Queue as MPQ

    return MPQ()


@pytest.fixture
def mock_result_initialized(mock_result_uninitialized):
    """Construct mock result object."""

    result_obj = deepcopy(mock_result_uninitialized)

    init_result_pre_dispatch(result_obj)
    return result_obj


def test_update_workflow_results_pattern_1(mocker, mock_result_initialized, mock_tasks_queue):
    """Test updating a workflow's results."""

    status = Result.RUNNING

    mock_result_initialized._status = status

    mock_get_result = mocker.patch(
        "app.core.update_workflow.get_result_object_from_result_service",
        return_value=mock_result_initialized,
    )
    mock_update_endtime = mocker.patch("app.core.update_workflow.update_workflow_endtime")
    mock_update_complete_workflow = mocker.patch(
        "app.core.update_workflow.update_completed_workflow"
    )
    mock_update_completed_tasks = mocker.patch("app.core.update_workflow.update_completed_tasks")

    ter = {"node_id": 0, "status": status, "output": "mock_output"}

    output = update_workflow_results(
        task_execution_results=ter, dispatch_id="mock_dispatch_id", tasks_queue=mock_tasks_queue
    )

    mock_get_result.assert_called_once()
    assert mock_update_endtime.mock_calls == []
    assert mock_update_complete_workflow.mock_calls == []
    assert mock_update_completed_tasks.mock_calls == []
    assert isinstance(output, Result)
    assert mock_result_initialized.status == status
    assert mock_result_initialized._get_node_output(0) == "mock_output"


@pytest.mark.parametrize(
    "status",
    [
        (Result.FAILED),
        (Result.CANCELLED),
    ],
)
def test_update_workflow_results_pattern_2(
    mocker, status, mock_result_initialized, mock_tasks_queue
):
    """Test updating a workflow's results."""

    mock_get_result = mocker.patch(
        "app.core.update_workflow.get_result_object_from_result_service",
        return_value=mock_result_initialized,
    )
    mock_update_endtime = mocker.patch(
        "app.core.update_workflow.update_workflow_endtime", return_value=mock_result_initialized
    )
    mock_update_complete_workflow = mocker.patch(
        "app.core.update_workflow.update_completed_workflow"
    )
    mock_update_completed_tasks = mocker.patch("app.core.update_workflow.update_completed_tasks")

    ter = {"node_id": 0, "status": status, "output": "mock_output"}

    output = update_workflow_results(
        task_execution_results=ter, dispatch_id="mock_dispatch_id", tasks_queue=mock_tasks_queue
    )

    mock_get_result.assert_called_once()
    mock_update_endtime.assert_called_once()
    assert mock_update_complete_workflow.mock_calls == []
    assert mock_update_completed_tasks.mock_calls == []
    assert isinstance(output, Result)
    assert mock_result_initialized.status == status
    assert mock_result_initialized._get_node_output(0) == "mock_output"


def test_update_workflow_results_pattern_3(mocker, mock_result_initialized, mock_tasks_queue):
    """Test updating a workflow's results."""

    mock_are_tasks_running = mocker.patch(
        "app.core.update_workflow.are_tasks_running", return_value=False
    )
    mock_get_result = mocker.patch(
        "app.core.update_workflow.get_result_object_from_result_service",
        return_value=mock_result_initialized,
    )
    mock_update_endtime = mocker.patch(
        "app.core.update_workflow.update_workflow_endtime", return_value=mock_result_initialized
    )
    mock_update_complete_workflow = mocker.patch(
        "app.core.update_workflow.update_completed_workflow"
    )
    mock_update_completed_tasks = mocker.patch("app.core.update_workflow.update_completed_tasks")

    ter = {"node_id": 0, "status": Result.COMPLETED, "output": "mock_output"}

    output = update_workflow_results(
        task_execution_results=ter, dispatch_id="mock_dispatch_id", tasks_queue=mock_tasks_queue
    )

    mock_are_tasks_running.assert_called_once()
    mock_get_result.assert_called_once()
    mock_update_endtime.assert_called_once()
    mock_update_complete_workflow.assert_called_once_with(mock_result_initialized)
    assert mock_update_completed_tasks.mock_calls == []
    assert isinstance(output, Result)
    assert mock_result_initialized._get_node_output(0) == "mock_output"


def test_update_workflow_results_pattern_4(mocker, mock_result_initialized, mock_tasks_queue):
    """Test updating a workflow's results."""

    mock_are_tasks_running = mocker.patch(
        "app.core.update_workflow.are_tasks_running", return_value=True
    )
    mock_get_result = mocker.patch(
        "app.core.update_workflow.get_result_object_from_result_service",
        return_value=mock_result_initialized,
    )
    mock_update_endtime = mocker.patch(
        "app.core.update_workflow.update_workflow_endtime", return_value=mock_result_initialized
    )
    mock_update_complete_workflow = mocker.patch(
        "app.core.update_workflow.update_completed_workflow"
    )
    mock_update_completed_tasks = mocker.patch("app.core.update_workflow.update_completed_tasks")

    ter = {"node_id": 0, "status": Result.COMPLETED, "output": "mock_output"}

    mock_tasks_queue.put([{"dispatch_id": [[0], [1, 2, 3], [4, 5], [6]]}])
    output = update_workflow_results(
        task_execution_results=ter, dispatch_id="mock_dispatch_id", tasks_queue=mock_tasks_queue
    )

    mock_are_tasks_running.assert_called_once()
    mock_get_result.assert_called_once()
    mock_update_endtime.assert_called_once()
    mock_update_completed_tasks.assert_called_once_with(
        "mock_dispatch_id", mock_tasks_queue, mock_result_initialized
    )
    assert mock_update_complete_workflow.mock_calls == []
    assert isinstance(output, Result)
    assert mock_result_initialized._get_node_output(0) == "mock_output"


def test_update_workflow_results_pattern_5(mocker, mock_result_initialized, mock_tasks_queue):
    """Test updating a workflow's results."""

    mock_are_tasks_running = mocker.patch(
        "app.core.update_workflow.are_tasks_running", return_value=True
    )
    mock_get_result = mocker.patch(
        "app.core.update_workflow.get_result_object_from_result_service",
        return_value=mock_result_initialized,
    )
    mock_update_endtime = mocker.patch(
        "app.core.update_workflow.update_workflow_endtime", return_value=mock_result_initialized
    )
    mock_update_complete_workflow = mocker.patch(
        "app.core.update_workflow.update_completed_workflow"
    )
    mock_update_completed_tasks = mocker.patch("app.core.update_workflow.update_completed_tasks")

    ter = {"node_id": 0, "status": Result.COMPLETED, "output": "mock_output"}

    mock_tasks_queue.put(None)
    output = update_workflow_results(
        task_execution_results=ter, dispatch_id="mock_dispatch_id", tasks_queue=mock_tasks_queue
    )

    mock_are_tasks_running.assert_called_once()
    mock_get_result.assert_called_once()
    mock_update_endtime.assert_called_once()
    assert mock_update_complete_workflow.mock_calls == []
    assert mock_update_completed_tasks.mock_calls == []
    assert isinstance(output, Result)
    assert mock_result_initialized._get_node_output(0) == "mock_output"


@pytest.mark.parametrize(
    "workflow_status,expected_endtime_type",
    [
        (Result.RUNNING, type(None)),
        (Result.NEW_OBJ, type(None)),
        (Result.FAILED, datetime),
        (Result.COMPLETED, datetime),
        (Result.CANCELLED, datetime),
    ],
)
def test_update_execution_endtime(
    mock_result_uninitialized, workflow_status, expected_endtime_type
):
    """Test update of the execution endtime."""

    mock_result_uninitialized._status = workflow_status

    output = update_workflow_endtime(mock_result_uninitialized)

    assert isinstance(output, Result)
    assert isinstance(mock_result_uninitialized._end_time, expected_endtime_type)


def test_update_completed_workflow_lattice(mocker, mock_result_initialized):
    """Test updating a completed lattice workflow's results."""

    mocker.patch("app.core.update_workflow._post_process", return_value="mock_result")
    mock_is_sublattice = mocker.patch(
        "app.core.update_workflow.is_sublattice_dispatch_id", return_value=False
    )
    mock_generate_task_result = mocker.patch(
        "app.core.update_workflow.generate_task_result", return_value={}
    )
    mock_send_task_update_to_dispatcher = mocker.patch(
        "app.core.update_workflow.send_task_update_to_dispatcher"
    )

    output = update_completed_workflow(mock_result_initialized)

    mock_is_sublattice.assert_called_once_with(mock_result_initialized.dispatch_id)

    assert mock_generate_task_result.mock_calls == []
    assert mock_send_task_update_to_dispatcher.mock_calls == []

    assert isinstance(output, Result)
    assert mock_result_initialized.status == Result.COMPLETED
    assert mock_result_initialized.result == "mock_result"


def test_update_completed_workflow_sublattice(mocker, mock_result_initialized):
    """Test updating a completed sublattice workflow's results."""

    mock_result_initialized._dispatch_id = "parent_dispatch_id:1"

    mocker.patch("app.core.update_workflow._post_process", return_value="mock_result")
    mock_is_sublattice = mocker.patch(
        "app.core.update_workflow.is_sublattice_dispatch_id", return_value=True
    )
    mock_generate_task_result = mocker.patch(
        "app.core.update_workflow.generate_task_result", return_value={}
    )
    mock_send_task_update_to_dispatcher = mocker.patch(
        "app.core.update_workflow.send_task_update_to_dispatcher"
    )

    output = update_completed_workflow(mock_result_initialized)

    mock_is_sublattice.assert_called_once_with(mock_result_initialized.dispatch_id)
    mock_generate_task_result.assert_called_once()
    mock_send_task_update_to_dispatcher.assert_called_once()

    assert isinstance(output, Result)
    assert mock_result_initialized.status == Result.COMPLETED
    assert mock_result_initialized.result == "mock_result"


def test_update_completed_electron_task(mocker, mock_result_initialized, mock_tasks_queue):
    """Test updating a completed task's results."""

    mock_get_result = mocker.patch(
        "app.core.update_workflow.get_result_object_from_result_service"
    )
    mock_dispatch_runnable_tasks = mocker.patch("app.core.update_workflow.dispatch_runnable_tasks")
    mock_send_result = mocker.patch(
        "app.core.update_workflow.send_result_object_to_result_service"
    )

    mock_tasks_queue.put([{"dispatch_id": [[0], [1, 2, 3], [4, 5], [6]]}])
    update_completed_tasks("dispatch_id", mock_tasks_queue, mock_result_initialized)

    assert mock_get_result.mock_calls == []
    assert mock_send_result.mock_calls == []
    mock_dispatch_runnable_tasks.assert_called_once_with(
        result_obj=mock_result_initialized,
        tasks_queue=mock_tasks_queue,
        task_order=[[0], [1, 2, 3], [4, 5], [6]],
    )


def test_update_completed_sublattice_task(mocker, mock_result_initialized, mock_tasks_queue):
    """Test updating a completed task's results."""

    mock_get_result = mocker.patch(
        "app.core.update_workflow.get_result_object_from_result_service",
        return_value="mock_sublattice_result",
    )
    mock_dispatch_runnable_tasks = mocker.patch("app.core.update_workflow.dispatch_runnable_tasks")
    mock_send_result = mocker.patch(
        "app.core.update_workflow.send_result_object_to_result_service"
    )

    mock_tasks_queue.put(
        [{"sublattice_dispatch_id": [[0], [1, 2]]}, {"dispatch_id": [[0], [1, 2, 3], [4, 5], [6]]}]
    )
    update_completed_tasks("dispatch_id", mock_tasks_queue, mock_result_initialized)

    mock_get_result.assert_called_once()
    mock_send_result.assert_called_once()
    print(mock_dispatch_runnable_tasks.mock_calls)
    mock_dispatch_runnable_tasks.assert_called_once_with(
        result_obj="mock_sublattice_result", tasks_queue=mock_tasks_queue, task_order=[[0], [1, 2]]
    )
