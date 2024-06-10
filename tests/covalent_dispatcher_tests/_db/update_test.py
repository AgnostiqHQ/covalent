# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import shutil
from datetime import datetime as dt
from pathlib import Path

import pytest

import covalent as ct
from covalent._results_manager.result import Result
from covalent._serialize.result import deserialize_result
from covalent._shared_files.defaults import WAIT_EDGE_NAME
from covalent._workflow.lattice import Lattice as LatticeClass
from covalent.executor import LocalExecutor
from covalent_dispatcher._dal.asset import local_store
from covalent_dispatcher._dal.exporters.result import export_result_manifest
from covalent_dispatcher._db import update, upsert
from covalent_dispatcher._db.datastore import DataStore
from covalent_dispatcher._db.models import Electron, ElectronDependency, Job, Lattice

# TEMP_RESULTS_DIR = "/tmp/results"
TEMP_RESULTS_DIR = os.environ.get("COVALENT_DATA_DIR") or ct.get_config("dispatcher.results_dir")
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

    # Deleting triggers since they are not needed in the db
    del workflow_1.metadata["triggers"]

    received_lattice = LatticeClass.deserialize_from_json(workflow_1.serialize_to_json())
    result = Result(lattice=received_lattice, dispatch_id="dispatch_1")
    result._initialize_nodes()
    return result


@pytest.fixture
def result_2():
    @ct.electron(executor="dask")
    def task(x):
        return x

    @ct.lattice(executor="local", workflow_executor="local")
    def workflow_2(x):
        return x

    Path(f"{TEMP_RESULTS_DIR}/dispatch_1").mkdir(parents=True, exist_ok=True)
    workflow_2.build_graph(x=2)
    received_lattice = LatticeClass.deserialize_from_json(workflow_2.serialize_to_json())
    result = Result(received_lattice, dispatch_id="dispatch_2")

    result._initialize_nodes()
    return result


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


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
        assert lattice_row.hooks_filename == upsert.LATTICE_HOOKS_FILENAME
        assert lattice_row.root_dispatch_id == "dispatch_1"
        assert lattice_row.results_dir == result_1.results_dir

        lattice_storage_path = Path(lattice_row.storage_path)
        assert Path(lattice_row.storage_path) == Path(TEMP_RESULTS_DIR) / "dispatch_1"

        workflow_function = local_store.load_file(
            storage_path=lattice_storage_path, filename=lattice_row.function_filename
        ).get_deserialized()
        assert workflow_function(1, 2) == 4
        with pytest.raises(FileNotFoundError):
            local_store.load_file(
                storage_path=lattice_storage_path, filename=lattice_row.error_filename
            )

        with pytest.raises(FileNotFoundError):
            local_store.load_file(
                storage_path=lattice_storage_path, filename=lattice_row.results_filename
            )

        executor_data = json.loads(lattice_row.executor_data)

        assert executor_data["short_name"] == le.short_name()
        assert executor_data["attributes"] == le.__dict__

        # Check that the electron records are as expected
        assert len(electron_rows) == 6
        for electron in electron_rows:
            assert electron.status == "NEW_OBJECT"
            assert electron.parent_lattice_id == 1
            assert electron.started_at is None and electron.completed_at is None

            if electron.transport_graph_node_id == 1:
                assert (
                    local_store.load_file(
                        storage_path=electron.storage_path, filename=electron.hooks_filename
                    )
                    == {}
                )
            if electron.transport_graph_node_id == 3:
                executor_data = json.loads(electron.executor_data)

                assert executor_data["short_name"] == le.short_name()
                assert executor_data["attributes"] == le.__dict__

        # Check that there are the appropriate amount of electron dependency records
        assert len(electron_dependency_rows) == 7

    # Tear down temporary results directory
    teardown_temp_results_dir(dispatch_id="dispatch_1")


@pytest.mark.parametrize("cancel_req", [False, True])
def test_result_persist_subworkflow_1(test_db, cancel_req, result_1, result_2, mocker):
    """Test the persist method for the Result object when passed an electron_id"""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    update.persist(result_1)

    with test_db.session() as session:
        electron = session.query(Electron).where(Electron.id == 1).first()
        job_record = session.query(Job).where(Job.id == Electron.job_id).first()
        job_record.cancel_requested = cancel_req

    update.persist(result_2, electron_id=1)

    # Query lattice / electron / electron dependency
    with test_db.session() as session:
        lattice_row = session.query(Lattice).where(Lattice.dispatch_id == "dispatch_2").first()
        electron_rows = session.query(Electron).where(Electron.parent_lattice_id == lattice_row.id)
        eids = [e.id for e in electron_rows]
        job_records = session.query(Job).where(Job.id.in_(eids)).all()

        # Check that lattice record is as expected
        assert lattice_row.dispatch_id == "dispatch_2"
        assert isinstance(lattice_row.created_at, dt)
        assert lattice_row.started_at is None
        assert isinstance(lattice_row.updated_at, dt) and isinstance(lattice_row.created_at, dt)
        assert lattice_row.completed_at is None
        assert lattice_row.status == "NEW_OBJECT"
        assert lattice_row.name == "workflow_2"
        assert lattice_row.electron_id == 1
        assert lattice_row.executor == "local"
        assert lattice_row.workflow_executor == "local"

        # Check the `cancel_requested` is propagated to sublattice

        for job in job_records:
            assert job.cancel_requested is cancel_req


def test_result_persist_rehydrate(test_db, result_1, mocker):
    """Test that persist followed by result_from preserves all result,
    lattice, and transport graph attributes"""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    update.persist(result_1)
    with test_db.session() as session:
        lattice_row = session.query(Lattice).first()
        manifest = export_result_manifest(result_1.dispatch_id)

        result_2 = deserialize_result(manifest)
        result_2._num_nodes = len(result_2.lattice.transport_graph._graph.nodes)

    assert result_1.__dict__.keys() == result_2.__dict__.keys()
    assert result_1.lattice.__dict__.keys() == result_2.lattice.__dict__.keys()

    tg_1 = result_1.lattice.transport_graph._graph
    tg_2 = result_2.lattice.transport_graph._graph

    assert list(tg_1.nodes) == list(tg_2.nodes)
    for n in tg_1.nodes:
        if "sublattice_result" not in tg_2.nodes[n]:
            tg_2.nodes[n]["sublattice_result"] = None
        if "function_string" not in tg_1.nodes[n]:
            tg_1.nodes[n]["function_string"] = ""
        if "workflow_executor" in tg_1.nodes[n]["metadata"]:
            del tg_1.nodes[n]["metadata"]["workflow_executor"]
            del tg_1.nodes[n]["metadata"]["workflow_executor_data"]
        if "workflow_executor" in tg_2.nodes[n]["metadata"]:
            del tg_2.nodes[n]["metadata"]["workflow_executor"]
            del tg_2.nodes[n]["metadata"]["workflow_executor_data"]
            assert set(tg_1.nodes[n].keys()).issubset(set(tg_2.nodes[n].keys()))

    assert tg_1.edges == tg_2.edges
    for e in tg_1.edges:
        if tg_1.edges[e]["edge_name"] != WAIT_EDGE_NAME:
            assert tg_1.edges[e] == tg_2.edges[e]
        else:
            assert tg_2.edges[e]["edge_name"] == WAIT_EDGE_NAME


def test_task_packing_persist(test_db, mocker):
    """Check that a job record is created per task group"""

    @ct.electron
    def task(arr):
        return sum(arr)

    @ct.lattice
    def workflow(arr):
        return task(arr)

    workflow.build_graph([1, 2, 3])

    received_lattice = LatticeClass.deserialize_from_json(workflow.serialize_to_json())
    result = Result(lattice=received_lattice, dispatch_id="test_task_packing_persist")
    result._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(result)
    tg = workflow.transport_graph
    task_groups = {tg.get_node_value(node_id, "task_group_id") for node_id in tg._graph.nodes}

    with test_db.session() as session:
        job_records = session.query(Job).all()
        assert len(job_records) == len(task_groups)


def test_cannot_persist_twice(test_db, mocker):
    """Check that an incoming dispatch can only be persisted once"""

    @ct.electron
    def task(arr):
        return sum(arr)

    @ct.lattice
    def workflow(arr):
        return task(arr)

    workflow.build_graph([1, 2, 3])

    received_lattice = LatticeClass.deserialize_from_json(workflow.serialize_to_json())
    result = Result(lattice=received_lattice, dispatch_id="test_task_packing_persist")
    result._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(result)

    with pytest.raises(RuntimeError):
        update.persist(result)
