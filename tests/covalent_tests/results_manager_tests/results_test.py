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

import os
import shutil
from datetime import datetime as dt
from pathlib import Path

import cloudpickle
import pytest
from sqlalchemy.orm import Session

import covalent as ct
from covalent._data_store.datastore import DataStore, DataStoreNotInitializedError
from covalent._data_store.models import Electron, ElectronDependency, Lattice
from covalent._results_manager.result import Result

TEMP_RESULTS_DIR = "/tmp"


def teardown_temp_results_dir(dispatch_id: str) -> None:
    """Method to tear down temporary results storage directory."""

    dir_path = f"{TEMP_RESULTS_DIR}/{dispatch_id}"
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)


@pytest.fixture
def db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


@pytest.fixture
def result_1():
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
    result = Result(lattice=workflow_1, results_dir=TEMP_RESULTS_DIR, dispatch_id="dispatch_1")
    result._initialize_nodes()
    return result


def test_result_no_db(result_1):
    with pytest.raises(DataStoreNotInitializedError):
        result_1.persist(db=None)


def test_result_persist_workflow_1(db, result_1):
    """Test the persist method for the Result object."""

    # Call Result.persist
    result_1.persist(db=db)

    # Query lattice / electron / electron dependency
    with Session(db.engine) as session:
        lattice_row = session.query(Lattice).first()
        electron_rows = session.query(Electron).all()
        electron_dependency_rows = session.query(ElectronDependency).all()

    # Check that lattice record is as expected
    assert lattice_row.dispatch_id == "dispatch_1"
    assert isinstance(lattice_row.created_at, dt)
    assert lattice_row.started_at is None
    assert isinstance(lattice_row.updated_at, dt) and isinstance(lattice_row.created_at, dt)
    assert lattice_row.completed_at is None
    assert lattice_row.status == "NEW_OBJECT"
    assert lattice_row.name == "workflow_1"
    assert lattice_row.electron_id is None

    lattice_storage_path = Path(lattice_row.storage_path)
    assert Path(lattice_row.storage_path) == Path(TEMP_RESULTS_DIR)

    with open(lattice_storage_path / lattice_row.function_filename, "rb") as f:
        workflow_function = cloudpickle.load(f)
    assert workflow_function(1, 2) == 4

    with open(lattice_storage_path / lattice_row.executor_filename, "rb") as f:
        executor_function = cloudpickle.load(f)
    assert executor_function == "dask"

    with open(lattice_storage_path / lattice_row.error_filename, "rb") as f:
        error_log = cloudpickle.load(f)
    assert error_log == result_1.error

    with open(lattice_storage_path / lattice_row.results_filename, "rb") as f:
        result = cloudpickle.load(f)
    assert result is None

    # Check that the electron records are as expected
    for electron in electron_rows:
        assert electron.status == "NEW_OBJECT"
        assert electron.parent_lattice_id == 1
        assert electron.started_at is None and electron.completed_at is None

    # Check that there are the appropriate amount of electron dependency records
    assert len(electron_dependency_rows) == 4

    # Update some node / lattice statuses
    cur_time = dt.now()
    result_1._end_time = cur_time
    result_1._status = "COMPLETED"
    result_1._result = {"helo": 1, "world": 2}

    for node_id in range(5):
        result_1._update_node(
            node_id=node_id,
            start_time=cur_time,
            end_time=cur_time,
            status="COMPLETED",
            # output={"test_data": "test_data"},  # TODO - Put back in later
            # sublattice_result=None,  # TODO - Add a test where this is not None
        )

    # Call Result.persist
    result_1.persist(db=db)

    # Query lattice / electron / electron dependency
    with Session(db.engine) as session:
        lattice_row = session.query(Lattice).first()
        electron_rows = session.query(Electron).all()
        electron_dependency_rows = session.query(ElectronDependency).all()
        print(f"THERE: {electron_dependency_rows}")

    # Check that the lattice records are as expected
    assert lattice_row.completed_at == cur_time
    assert lattice_row.status == "COMPLETED"

    with open(lattice_storage_path / lattice_row.results_filename, "rb") as f:
        result = cloudpickle.load(f)
    assert result_1.result == result

    # Check that the electron records are as expected
    for electron in electron_rows:
        assert electron.status == "COMPLETED"
        assert electron.parent_lattice_id == 1
        assert electron.started_at == electron.completed_at == cur_time
        assert Path(electron.storage_path) == Path(
            f"{TEMP_RESULTS_DIR}/node_{electron.transport_graph_node_id}"
        )

    # Tear down temporary results directory
    teardown_temp_results_dir(dispatch_id="dispatch_1")
