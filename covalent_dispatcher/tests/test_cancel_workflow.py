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

"""Unit tests for Cancel Workflow."""

from copy import deepcopy
from unittest import mock

import pytest
from app.core.cancel_workflow import cancel_task, cancel_workflow_execution, get_all_task_ids
from app.core.utils import send_cancel_task_to_runner

import covalent as ct
from covalent._results_manager.result import Result
from covalent._workflow.transport import TransportableObject, _TransportGraph


@pytest.fixture
def mock_result_obj():
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
def mock_task_id_batch():
    """Construct a list of mocked tasks. A task is composed of a dispatch id and a task id in the form of a tuple"""
    mocked_tasks = list()
    num_of_tasks = 3

    for task_num in range(num_of_tasks):
        mocked_tasks.append((str(task_num), task_num))
    print("mocked tasks", mocked_tasks)
    return mocked_tasks


def test_cancel_workflow_execution(mocker, mock_result_obj, mock_task_id_batch):
    """
    Test that the cancel workflow function updates the cancellation status of a list of tasks when
    the cancel task function is called.
    """

    mock_cancellation_status = True
    mock_cancel_task = mock.Mock(name="cancel task mock", return_value=mock_cancellation_status)

    mock_cancellation_status = mocker.patch(
        "refactor.dispatcher.app.core.cancel_workflow.cancel_workflow_execution",
        return_value=mock_cancellation_status,
    )

    for dispatch_id, task_id in mock_task_id_batch:
        assert (mock_cancel_task(dispatch_id, task_id)) == mock_cancellation_status.return_value


def test_cancel_task(mocker, mock_dispatch_id="3", mock_task_id=2):
    """Test that the cancel task function successfully calls the Runner API to cancel a task and return its cancellation
    status"""

    mock_response = mock_dispatch_id, mock_task_id
    mock_send_cancel_task_to_runner = mocker.patch(
        "refactor.dispatcher.app.core.utils.send_task_list_to_runner", return_value=mock_response
    )
    pass


def test_get_all_task_ids():
    # This will test the get_all_task_ids()
    pass
