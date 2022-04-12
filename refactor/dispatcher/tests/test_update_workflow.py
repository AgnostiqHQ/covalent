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

import pytest
from app.core.update_workflow import (
    _update_completed_tasks,
    _update_completed_workflow,
    _update_workflow_endtime,
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


def test_update_workflow_results():
    """Test updating a workflow's results."""

    pass


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

    output = _update_workflow_endtime(mock_result_uninitialized)

    assert isinstance(output, Result)
    assert isinstance(mock_result_uninitialized._end_time, expected_endtime_type)


def test_update_completed_workflow():
    """Test updating a completed workflow's results."""

    pass


def test_update_completed_task():
    """Test updating a completed task's results."""

    pass
