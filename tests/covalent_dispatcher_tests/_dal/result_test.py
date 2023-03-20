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

"""Tests for DB-backed Result"""


import os
from datetime import datetime

import pytest

import covalent as ct
from covalent._results_manager import Result as SDKResult
from covalent._workflow.lattice import Lattice as SDKLattice
from covalent_dispatcher._dal.lattice import ASSET_KEYS as LATTICE_ASSET_KEYS
from covalent_dispatcher._dal.result import ASSET_KEYS, METADATA_KEYS, Result, get_result_object
from covalent_dispatcher._db import models, update
from covalent_dispatcher._db.datastore import DataStore

TEMP_RESULTS_DIR = os.environ.get("COVALENT_DATA_DIR") or ct.get_config("dispatcher.results_dir")


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def get_mock_result() -> SDKResult:
    """Construct a mock result object corresponding to a lattice."""

    @ct.electron(executor="local")
    def task(x):
        return x

    @ct.lattice(deps_bash=ct.DepsBash(["ls"]))
    def workflow(x):
        res1 = task(x)
        return res1

    workflow.build_graph(x=1)
    received_workflow = SDKLattice.deserialize_from_json(workflow.serialize_to_json())
    result_object = SDKResult(received_workflow, "mock_dispatch")

    return result_object


def test_result_attributes(test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )

        srvres = Result(session, record)
        asset_ids = srvres.get_asset_ids(session, [])

    meta = srvres.metadata.keys()
    assert METADATA_KEYS.issubset(meta)
    assert asset_ids.keys() == ASSET_KEYS.union(LATTICE_ASSET_KEYS)


def test_result_restricted_attributes(test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )

        srvres = Result(session, record, bare=True, keys=["status", "dispatch_id"])

    meta = srvres.metadata.keys()
    assert "status" in meta
    assert "dispatch_id" in meta
    assert "root_dispatch_id" not in meta


def test_result_get_set_value(test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )

        srvres = Result(session, record)

    assert srvres.status == SDKResult.NEW_OBJ

    start_time = datetime.now()
    end_time = datetime.now()

    srvres._update_dispatch(
        start_time=start_time,
        end_time=end_time,
        status=SDKResult.RUNNING,
        error="RuntimeException",
        result=5,
    )
    srvres._status = SDKResult.RUNNING
    srvres._error = "RuntimeException"
    srvres._result = 5
    srvres.commit()

    assert srvres.start_time == start_time
    assert srvres.end_time == end_time
    assert srvres.error == "RuntimeException"
    assert srvres.status == SDKResult.RUNNING
    assert srvres.result == 5


def test_result_update_node(test_db, mocker):
    import datetime

    from covalent._workflow.transport import TransportableObject

    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )

        srvres = Result(session, record)

    timestamp = datetime.datetime.now()

    node_result = {
        "node_id": 1,
        "start_time": timestamp,
        "end_time": timestamp,
        "output": TransportableObject(1),
        "status": SDKResult.COMPLETED,
        "stdout": "Hello\n",
        "stderr": "Bye\n",
    }

    srvres._update_node(**node_result)

    tg = srvres.lattice.transport_graph
    assert tg.get_node_value(1, "start_time") == timestamp
    assert tg.get_node_value(1, "end_time") == timestamp
    assert tg.get_node_value(1, "status") == SDKResult.COMPLETED
    assert tg.get_node_value(1, "output").get_deserialized() == 1
    assert tg.get_node_value(1, "stdout") == "Hello\n"
    assert tg.get_node_value(1, "stderr") == "Bye\n"

    assert srvres.get_value("completed_electron_num") == 1


def test_result_update_node_2(test_db, mocker):
    """Adapted from update_test.py"""

    import datetime

    from covalent._workflow.transport import TransportableObject
    from covalent_dispatcher._db.write_result_to_db import load_file

    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )

        srvres = Result(session, record)

    timestamp = datetime.datetime.now()
    srvres._update_node(
        node_id=0,
        node_name="test_name",
        start_time=timestamp,
        status="RUNNING",
        error="test_error",
        stdout="test_stdout",
        stderr="test_stderr",
    )

    with test_db.session() as session:
        lattice_record = session.query(models.Lattice).first()
        electron_record = (
            session.query(models.Electron)
            .where(models.Electron.transport_graph_node_id == 0)
            .first()
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

        assert srvres.lattice.transport_graph.get_node_value(0, "error") == "test_error"

        assert lattice_record.electron_num == 3
        assert lattice_record.completed_electron_num == 0
        assert lattice_record.updated_at is not None

    srvres._update_node(
        node_id=0,
        end_time=timestamp,
        status=SDKResult.COMPLETED,
        output=5,
    )

    with test_db.session() as session:
        lattice_record = session.query(models.Lattice).first()
        electron_record = (
            session.query(models.Electron)
            .where(models.Electron.transport_graph_node_id == 0)
            .first()
        )

        assert electron_record.status == "COMPLETED"
        assert electron_record.completed_at is not None
        assert electron_record.updated_at is not None

        result = load_file(
            storage_path=electron_record.storage_path, filename=electron_record.results_filename
        )
        assert result == 5

        assert lattice_record.electron_num == 3
        assert lattice_record.completed_electron_num == 1
        assert lattice_record.updated_at is not None


def test_get_result_object(test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    res_obj = get_result_object("mock_dispatch")
    assert res_obj.dispatch_id == "mock_dispatch"

    # Get bare result object
    res_obj = get_result_object("mock_dispatch", True)
    assert res_obj.lattice.transport_graph.bare

    with pytest.raises(KeyError):
        get_result_object("nonexistent_dispatch")


def test_get_failed_nodes(test_db, mocker):
    from covalent._workflow.transport import TransportableObject

    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )

        srvres = Result(session, record)

    srvres.lattice.transport_graph.set_node_value(0, "status", SDKResult.FAILED)

    failed_nodes = srvres._get_failed_nodes()
    assert len(failed_nodes) == 1
    assert failed_nodes[0] == (0, "task")


def test_get_all_node_outputs(test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )

        srvres = Result(session, record)

    srvres.lattice.transport_graph.set_node_value(0, "output", 25)
    srvres.lattice.transport_graph.set_node_value(1, "output", 5)
    srvres.lattice.transport_graph.set_node_value(2, "output", 25)
    node_outputs = srvres.get_all_node_outputs()

    expected_outputs = [25, 5, 25]
    for i, item in enumerate(node_outputs.items()):
        key, val = item
        assert expected_outputs[i] == val
