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
import os
import shutil
from datetime import datetime as dt
from datetime import timezone
from pathlib import Path

import pytest

import covalent as ct
from covalent._results_manager.result import Result
from covalent._workflow.lattice import Lattice as LatticeClass
from covalent.executor import LocalExecutor
from covalent_dispatcher._db import update, upsert
from covalent_dispatcher._db.datastore import DataStore
from covalent_dispatcher._db.models import Electron, ElectronDependency, Lattice
from covalent_dispatcher._db.write_result_to_db import load_file
from covalent_dispatcher._service.app import _result_from

TEMP_RESULTS_DIR = "/tmp/results"
le = LocalExecutor(log_stdout="/tmp/stdout.log")


def teardown_temp_results_dir(dispatch_id: str) -> None:
    """Method to tear down temporary results storage directory."""

    dir_path = f"{TEMP_RESULTS_DIR}/{dispatch_id}"
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)


@pytest.fixture
def result_1():
    @ct.electron(executor="dask")
    def task_1(x, y):
        return x * y

    @ct.electron(executor=le)
    def task_2(x, y):
        return x + y

    @ct.lattice(executor=le, workflow_executor=le)
    def workflow_1(a, b):
        """Docstring"""
        res_1 = task_1(a, b)
        return task_2(res_1, b)

    Path(f"{TEMP_RESULTS_DIR}/dispatch_1").mkdir(parents=True, exist_ok=True)
    workflow_1.build_graph(a=1, b=2)
    received_lattice = LatticeClass.deserialize_from_json(workflow_1.serialize_to_json())
    result = Result(lattice=received_lattice, dispatch_id="dispatch_1")
    #    result.lattice.metadata["results_dir"] = TEMP_RESULTS_DIR
    result._initialize_nodes()
    return result


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def test_update_node(test_db, result_1, mocker):
    """Test the node update method."""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    update.persist(result_1)
    update._node(
        result_1,
        node_id=0,
        node_name="test_name",
        start_time=dt.now(timezone.utc),
        status="RUNNING",
        error="test_error",
        sublattice_result="test_sublattice",
        stdout="test_stdout",
        stderr="test_stderr",
    )

    with test_db.session() as session:
        lattice_record = session.query(Lattice).first()
        electron_record = (
            session.query(Electron).where(Electron.transport_graph_node_id == 0).first()
        )

        assert electron_record.name == "test_name"
        assert electron_record.status == "RUNNING"
        assert electron_record.started_at is not None

        stdout = load_file(
            storage_path=electron_record.storage_path, filename=electron_record.stdout_filename
        )
        assert stdout == "test_stdout"

        stderr = load_file(
            storage_path=electron_record.storage_path, filename=electron_record.stderr_filename
        )
        assert stderr == "test_stderr"

        assert result_1.lattice.transport_graph.get_node_value(0, "error") == "test_error"
        assert (
            result_1.lattice.transport_graph.get_node_value(0, "sublattice_result")
            == "test_sublattice"
        )

        assert lattice_record.electron_num == 5
        assert lattice_record.completed_electron_num == 0
        assert lattice_record.updated_at is not None
    update._node(
        result_1,
        node_id=0,
        end_time=dt.now(timezone.utc),
        status=Result.COMPLETED,
        output=5,
    )

    with test_db.session() as session:
        lattice_record = session.query(Lattice).first()
        electron_record = (
            session.query(Electron).where(Electron.transport_graph_node_id == 0).first()
        )

        assert electron_record.status == "COMPLETED"
        assert electron_record.completed_at is not None
        assert electron_record.updated_at is not None

        result = load_file(
            storage_path=electron_record.storage_path, filename=electron_record.results_filename
        )
        assert result == 5

        assert lattice_record.electron_num == 5
        assert lattice_record.completed_electron_num == 1
        assert lattice_record.updated_at is not None


def test_result_persist_workflow_1(test_db, result_1, mocker):
    """Test the persist method for the Result object."""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    update.persist(result_1)

    # Query lattice / electron / electron dependency
    with test_db.session() as session:
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
        assert lattice_row.executor == "local"
        assert lattice_row.workflow_executor == "local"
        assert lattice_row.deps_filename == upsert.LATTICE_DEPS_FILENAME
        assert lattice_row.call_before_filename == upsert.LATTICE_CALL_BEFORE_FILENAME
        assert lattice_row.call_after_filename == upsert.LATTICE_CALL_AFTER_FILENAME
        assert lattice_row.root_dispatch_id == "dispatch_1"
        assert lattice_row.results_dir == result_1.results_dir

        lattice_storage_path = Path(lattice_row.storage_path)
        assert Path(lattice_row.storage_path) == Path(TEMP_RESULTS_DIR) / "dispatch_1"

        workflow_function = load_file(
            storage_path=lattice_storage_path, filename=lattice_row.function_filename
        ).get_deserialized()
        assert workflow_function(1, 2) == 4
        assert (
            load_file(storage_path=lattice_storage_path, filename=lattice_row.error_filename) == ""
        )
        assert (
            load_file(
                storage_path=lattice_storage_path, filename=lattice_row.results_filename
            ).get_deserialized()
            is None
        )

        executor_data = load_file(
            storage_path=lattice_storage_path, filename=lattice_row.executor_data_filename
        )

        assert executor_data["short_name"] == le.short_name()
        assert executor_data["attributes"] == le.__dict__

        saved_named_args = load_file(
            storage_path=lattice_storage_path, filename=lattice_row.named_args_filename
        )

        saved_named_kwargs = load_file(
            storage_path=lattice_storage_path, filename=lattice_row.named_kwargs_filename
        )
        saved_named_args_raw = {k: v.get_deserialized() for k, v in saved_named_args.items()}
        saved_named_kwargs_raw = {k: v.get_deserialized() for k, v in saved_named_kwargs.items()}

        assert saved_named_args_raw == {}
        assert saved_named_kwargs_raw == {"a": 1, "b": 2}

        # Check that the electron records are as expected
        for electron in electron_rows:
            assert electron.status == "NEW_OBJECT"
            assert electron.parent_lattice_id == 1
            assert electron.started_at is None and electron.completed_at is None

            if electron.transport_graph_node_id == 1:
                assert (
                    load_file(storage_path=electron.storage_path, filename=electron.deps_filename)
                    == {}
                )
                assert (
                    load_file(
                        storage_path=electron.storage_path, filename=electron.call_before_filename
                    )
                    == []
                )
                assert (
                    load_file(
                        storage_path=electron.storage_path, filename=electron.call_after_filename
                    )
                    == []
                )
            if electron.transport_graph_node_id == 3:
                executor_data = load_file(
                    storage_path=electron.storage_path, filename=electron.executor_data_filename
                )

                assert executor_data["short_name"] == le.short_name()
                assert executor_data["attributes"] == le.__dict__

        # Check that there are the appropriate amount of electron dependency records
        assert len(electron_dependency_rows) == 4

        # Update some node / lattice statuses
        cur_time = dt.now(timezone.utc)
        result_1._end_time = cur_time
        result_1._status = "COMPLETED"
        result_1._result = ct.TransportableObject({"helo": 1, "world": 2})

        for node_id in range(5):
            update._node(
                result_1,
                node_id=node_id,
                start_time=cur_time,
                end_time=cur_time,
                status="COMPLETED",
                # output={"test_data": "test_data"},  # TODO - Put back in later
                # sublattice_result=None,  # TODO - Add a test where this is not None
            )

        # Call Result.persist
        update.persist(result_1)

    # Query lattice / electron / electron dependency
    with test_db.session() as session:
        lattice_row = session.query(Lattice).first()
        electron_rows = session.query(Electron).all()
        electron_dependency_rows = session.query(ElectronDependency).all()

        # Check that the lattice records are as expected
        assert lattice_row.completed_at.strftime("%Y-%m-%d %H:%M") == cur_time.strftime(
            "%Y-%m-%d %H:%M"
        )
        assert lattice_row.status == "COMPLETED"
        result = load_file(
            storage_path=lattice_storage_path, filename=lattice_row.results_filename
        )
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


def test_result_persist_subworkflow_1(test_db, result_1, mocker):
    """Test the persist method for the Result object when passed an electron_id"""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    update.persist(result_1, electron_id=2)

    # Query lattice / electron / electron dependency
    with test_db.session() as session:
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
        assert lattice_row.electron_id == 2
        assert lattice_row.executor == "local"
        assert lattice_row.workflow_executor == "local"


def test_result_persist_rehydrate(test_db, result_1, mocker):
    """Test that persist followed by result_from preserves all result,
    lattice, and transport graph attributes"""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    update.persist(result_1)
    with test_db.session() as session:
        lattice_row = session.query(Lattice).first()
        result_2 = _result_from(lattice_row)

    assert result_1.__dict__.keys() == result_2.__dict__.keys()
    assert result_1.lattice.__dict__.keys() == result_2.lattice.__dict__.keys()
    for key in result_1.lattice.__dict__.keys():
        if key == "transport_graph":
            continue
        assert result_1.lattice.__dict__[key] == result_2.lattice.__dict__[key]

    for key in result_1.__dict__.keys():
        if key == "_lattice":
            continue
        assert result_1.__dict__[key] == result_2.__dict__[key]

    tg_1 = result_1.lattice.transport_graph._graph
    tg_2 = result_2.lattice.transport_graph._graph

    assert tg_1.nodes == tg_2.nodes
    for n in tg_1.nodes:
        assert tg_1.nodes[n].keys() == tg_2.nodes[n].keys()
        for k in tg_1.nodes[n]:
            assert tg_1.nodes[n][k] == tg_2.nodes[n][k]

    assert tg_1.edges == tg_2.edges
    for e in tg_1.edges:
        assert tg_1.edges[e] == tg_2.edges[e]


def test_lattice_persist(result_1):
    update.persist(result_1.lattice)
    assert result_1.lattice.transport_graph.dirty_nodes == []


def test_transport_graph_persist(result_1):
    update.persist(result_1.lattice.transport_graph)
    assert result_1.lattice.transport_graph.dirty_nodes == []
