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

"""Unit tests for the Result object."""

import pytest
from sqlalchemy.orm import Session

import covalent as ct
from covalent._data_store.datastore import DataStore
from covalent._results_manager.result import Result


def build_temp_results_dir() -> str:
    """Method to build a temporary results storage directory."""

    return None


def teardown_temp_results_dir():
    """Method to tear down temporary results storage directory."""

    pass


@pytest.fixture
def db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


@pytest.fixture
def result_1():

    temp_results_dir = build_temp_results_dir()

    @ct.electron
    def task_1(x, y):
        return x * y

    @ct.electron
    def task_2(x, y):
        return x + y

    @ct.lattice
    def workflow_1(a, b):
        res_1 = task_1(a, b)
        return task_2(res_1, b)

    workflow_1.build_graph(a=1, b=2)
    return Result(lattice=workflow_1, results_dir=temp_results_dir, dispatch_id="dispatch_1")


def test_result_persist_workflow_1(db, result_1):
    """Test the persist method for the Result object."""

    # TODO - call Result.persist
    result_1.persist(db=db, _in_memory=True)

    # TODO - Query lattice / electron / electron dependency

    # TODO - Check via assert statements that the records are what they should be

    # TODO - update some node / lattice statuses

    # TODO - Query lattice / electron / electron dependency

    # TODO - Check via assert statements that the records are what they should be

    # Tear down temporary results directory
    teardown_temp_results_dir()
