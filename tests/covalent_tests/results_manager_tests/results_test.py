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
from datetime import timezone
from pathlib import Path
from unicodedata import name

import cloudpickle
import pytest
from sqlalchemy.orm import Session

import covalent as ct
from covalent._data_store.datastore import DataStore, DataStoreNotInitializedError
from covalent._data_store.models import Electron, ElectronDependency, Lattice
from covalent._results_manager.result import Result

TEMP_RESULTS_DIR = "/tmp/results"


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
    @ct.electron(executor="dask")
    def task_1(x, y):
        return x * y

    @ct.electron(executor="dask")
    def task_2(x, y):
        return x + y

    @ct.lattice(executor="dask")
    def workflow_1(a, b):
        res_1 = task_1(a, b)
        return task_2(res_1, b)

    Path(f"{TEMP_RESULTS_DIR}/dispatch_1").mkdir(parents=True, exist_ok=True)
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
    assert Path(lattice_row.storage_path) == Path(TEMP_RESULTS_DIR) / "dispatch_1"

    with open(lattice_storage_path / lattice_row.function_filename, "rb") as f:
        workflow_function = cloudpickle.load(f).get_deserialized()
    assert workflow_function(1, 2) == 4

    with open(lattice_storage_path / lattice_row.executor_filename, "rb") as f:
        executor_function = cloudpickle.load(f)
    assert executor_function == "dask"

    with open(lattice_storage_path / lattice_row.error_filename, "rb") as f:
        error_log = cloudpickle.load(f)
    assert error_log == result_1.error

    with open(lattice_storage_path / lattice_row.results_filename, "rb") as f:
        result = cloudpickle.load(f)
    assert result.get_deserialized() is None

    # Check that the electron records are as expected
    for electron in electron_rows:
        assert electron.status == "NEW_OBJECT"
        assert electron.parent_lattice_id == 1
        assert electron.started_at is None and electron.completed_at is None

        if electron.transport_graph_node_id == 1:
            with open(Path(electron.storage_path) / electron.deps_filename, "rb") as f:
                deps = cloudpickle.load(f)
                assert deps == {}

            with open(Path(electron.storage_path) / electron.call_before_filename, "rb") as f:
                call_before = cloudpickle.load(f)
                assert call_before == []

            with open(Path(electron.storage_path) / electron.call_after_filename, "rb") as f:
                call_after = cloudpickle.load(f)
                assert call_after == []

            with open(Path(electron.storage_path) / electron.key_filename, "rb") as f:
                key = cloudpickle.load(f)
                assert key is None

    # Check that there are the appropriate amount of electron dependency records
    assert len(electron_dependency_rows) == 4

    # Update some node / lattice statuses
    cur_time = dt.now(timezone.utc)
    result_1._end_time = cur_time
    result_1._status = "COMPLETED"
    result_1._result = ct.TransportableObject({"helo": 1, "world": 2})

    for node_id in range(5):
        result_1._update_node(
            db=db,
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

    # Check that the lattice records are as expected
    assert lattice_row.completed_at.strftime("%Y-%m-%d %H:%M") == cur_time.strftime(
        "%Y-%m-%d %H:%M"
    )
    assert lattice_row.status == "COMPLETED"

    with open(lattice_storage_path / lattice_row.results_filename, "rb") as f:
        result = cloudpickle.load(f)
    assert result_1.result == result.get_deserialized()

    # Check that the electron records are as expected
    for electron in electron_rows:
        assert electron.status == "COMPLETED"
        assert electron.parent_lattice_id == 1
        assert (
            electron.started_at.strftime("%Y-%m-%d %H:%M")
            == electron.completed_at.strftime("%Y-%m-%d %H:%M")
            == cur_time.strftime("%Y-%m-%d %H:%M")
        )
        assert Path(electron.storage_path) == Path(
            f"{TEMP_RESULTS_DIR}/dispatch_1/node_{electron.transport_graph_node_id}"
        )

    # Tear down temporary results directory
    teardown_temp_results_dir(dispatch_id="dispatch_1")


def test_get_node_error(db, result_1):
    """Test result method to get the node error."""

    result_1.persist(db)
    assert result_1._get_node_error(db=db, node_id=0) is None


def test_get_node_value(db, result_1):
    """Test result method to get the node value."""

    result_1.persist(db)
    assert result_1._get_node_value(db=db, node_id=0) is None


def test_get_all_node_results(db, result_1):
    """Test result method to get all the node results."""

    result_1.persist(db)
    for data_row in result_1.get_all_node_results(db):
        if data_row["node_id"] == 0:
            assert data_row["node_name"] == "task_1"
        elif data_row["node_id"] == 1:
            assert data_row["node_name"] == ":parameter:1"


def test_update_node(db, result_1):
    """Test the node update method."""

    # Call Result.persist
    result_1.persist(db=db)

    result_1._update_node(
        db=db,
        node_id=0,
        node_name="test_name",
        start_time=dt.now(timezone.utc),
        status="RUNNING",
        error="test_error",
        sublattice_result="test_sublattice",
        stdout="test_stdout",
        stderr="test_stderr",
    )

    with Session(db.engine) as session:
        lattice_record = session.query(Lattice).first()
        electron_record = (
            session.query(Electron).where(Electron.transport_graph_node_id == 0).first()
        )

    assert electron_record.name == "test_name"
    assert electron_record.status == "RUNNING"
    assert electron_record.started_at is not None

    with open(Path(electron_record.storage_path) / electron_record.stdout_filename, "rb") as f:
        stdout = cloudpickle.load(f)
        assert stdout == "test_stdout"

    with open(Path(electron_record.storage_path) / electron_record.stderr_filename, "rb") as f:
        stderr = cloudpickle.load(f)
        assert stderr == "test_stderr"

    assert result_1.lattice.transport_graph.get_node_value(0, "error") == "test_error"
    assert (
        result_1.lattice.transport_graph.get_node_value(0, "sublattice_result")
        == "test_sublattice"
    )

    assert lattice_record.electron_num == 5
    assert lattice_record.completed_electron_num == 0
    assert lattice_record.updated_at is not None

    result_1._update_node(
        db=db,
        node_id=0,
        end_time=dt.now(timezone.utc),
        status="COMPLETED",
        output=5,
    )

    with Session(db.engine) as session:
        lattice_record = session.query(Lattice).first()
        electron_record = (
            session.query(Electron).where(Electron.transport_graph_node_id == 0).first()
        )

    assert electron_record.status == "COMPLETED"
    assert electron_record.completed_at is not None
    assert electron_record.updated_at is not None

    with open(Path(electron_record.storage_path) / electron_record.results_filename, "rb") as f:
        result = cloudpickle.load(f)
        assert result == 5

    assert lattice_record.electron_num == 5
    assert lattice_record.completed_electron_num == 1
    assert lattice_record.updated_at is not None
