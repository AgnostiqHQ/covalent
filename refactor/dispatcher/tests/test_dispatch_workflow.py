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

import pytest
from app.core.dispatch_workflow import init_result_pre_dispatch

import covalent as ct
from covalent._results_manager.result import Result


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

    return Result(lattice=workflow, results_dir="", dispatch_id="mock_dispatch_id")


@pytest.fixture
def mock_result_initialized(mock_result_uninitialized):
    """Construct mock result object."""

    return init_result_pre_dispatch(mock_result_uninitialized)


def test_dispatch_workflow_func():
    pass


def test_dispatch_runnable_tasks():
    pass


def test_start_dispatch():
    pass


def test_get_runnable_tasks():
    pass


def test_init_result_pre_dispatch():
    pass


def test_run_tasks():
    pass


def test_is_runnable_task(mock_result_initialized):
    """Test function that returns status of whether a task is runnable."""

    result_obj = mock_result_uninitialized
    print(result_obj)
