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

"""Tests for DB-backed Result"""


import os
from datetime import datetime

import pytest

import covalent as ct
from covalent._results_manager import Result as SDKResult
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._workflow.lattice import Lattice as SDKLattice
from covalent._workflow.transportable_object import TransportableObject
from covalent_dispatcher._dal.electron import ASSET_KEYS as ELECTRON_ASSET_KEYS
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

    meta = srvres.metadata_keys
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

    meta = srvres.query_keys
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
        result=TransportableObject(5),
    )

    assert srvres.start_time == start_time
    assert srvres.end_time == end_time
    assert srvres.error == "RuntimeException"
    assert srvres.status == SDKResult.RUNNING
    assert srvres.result.get_deserialized() == 5


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
    from covalent_dispatcher._dal.asset import local_store

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

        stdout = local_store.load_file(
            storage_path=electron_record.storage_path, filename=electron_record.stdout_filename
        )
        assert stdout == "test_stdout"

        stderr = local_store.load_file(
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
        output=TransportableObject(5),
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

        result = local_store.load_file(
            storage_path=electron_record.storage_path, filename=electron_record.results_filename
        )
        assert result.get_deserialized() == 5

        assert lattice_record.electron_num == 3
        assert lattice_record.completed_electron_num == 1
        assert lattice_record.updated_at is not None


def test_result_update_node_handles_postprocessing(test_db, mocker):
    """Check postprocessing node updates."""

    import datetime

    from covalent._workflow.transport import TransportableObject

    res = get_mock_result()
    res._initialize_nodes()

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
        "node_id": 2,
        "start_time": timestamp,
        "end_time": timestamp,
        "output": TransportableObject(1),
        "status": SDKResult.COMPLETED,
        "stdout": "Hello\n",
        "stderr": "Bye\n",
    }

    srvres._update_node(**node_result)

    # Output of postprocessing electron should be set as the dispatch
    # output.
    assert srvres.get_value("status") == SDKResult.COMPLETED
    assert srvres.get_value("result").get_deserialized() == 1


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

    srvres.lattice.transport_graph.set_node_value(0, "output", TransportableObject(25))
    srvres.lattice.transport_graph.set_node_value(1, "output", TransportableObject(5))
    srvres.lattice.transport_graph.set_node_value(2, "output", TransportableObject(25))
    node_outputs = srvres.get_all_node_outputs()

    expected_outputs = [25, 5, 25]
    for i, item in enumerate(node_outputs.items()):
        key, val = item
        assert expected_outputs[i] == val.get_deserialized()


def test_get_linked_assets(test_db, mocker):
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

        assets = srvres.get_all_assets()

    num_nodes = len(res.lattice.transport_graph._graph.nodes)
    assert len(assets["lattice"]) == len(ASSET_KEYS) + len(LATTICE_ASSET_KEYS)
    assert len(assets["nodes"]) == num_nodes * len(ELECTRON_ASSET_KEYS)


def test_result_ensure_run_once(test_db, mocker):
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

    assert srvres.status == RESULT_STATUS.NEW_OBJECT
    assert Result.ensure_run_once("mock_dispatch") is True
    assert srvres.status == RESULT_STATUS.STARTING
    assert Result.ensure_run_once("mock_dispatch") is False
    assert srvres.status == RESULT_STATUS.STARTING


def test_result_filters_illegal_status_updates(test_db, mocker):
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

    first_update = srvres._update_node(0, status=RESULT_STATUS.RUNNING)
    second_update = srvres._update_node(0, status=RESULT_STATUS.COMPLETED)
    third_update = srvres._update_node(0, status=RESULT_STATUS.COMPLETED)

    assert first_update and second_update
    assert not third_update


def test_result_filters_parent_electron_updates(test_db, mocker):
    """Check filtering of status updates for sublattice electrons"""

    res = get_mock_result()
    sub_res = get_mock_result()
    res.lattice.transport_graph.set_node_value(0, "name", ":sublattice:")
    sub_res._dispatch_id = "sub_mock_dispatch"
    res._initialize_nodes()
    sub_res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)
    update.persist(sub_res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )
        sub_record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "sub_mock_dispatch")
            .first()
        )

        srvres = Result(session, record)
        subl_node = srvres.lattice.transport_graph.get_node(0, session)

        sub_srvres = Result(session, sub_record)
        sub_srvres.set_value("electron_id", subl_node._electron_id, session)
        sub_srvres._electron_id = subl_node._electron_id

    sub_srvres._update_dispatch(status=RESULT_STATUS.RUNNING)

    assert subl_node.get_value("sub_dispatch_id") == sub_res._dispatch_id

    first_update = srvres._update_node(0, status=RESULT_STATUS.RUNNING)

    # This should fail because the electron status doesn't match the subdispatch
    second_update = srvres._update_node(0, status=RESULT_STATUS.COMPLETED)
    sub_srvres.set_value("result", TransportableObject(42))
    sub_srvres._update_dispatch(status=RESULT_STATUS.COMPLETED)

    # This should now succeed.
    third_update = srvres._update_node(0, status=RESULT_STATUS.COMPLETED)

    assert first_update
    assert not second_update
    assert third_update

    assert subl_node.get_value("output").get_deserialized() == 42


def test_result_controller_bulk_get(test_db, mocker):
    record_1 = models.Lattice(
        dispatch_id="dispatch_1",
        root_dispatch_id="dispatch_1",
        name="dispatch_1",
        status="NEW_OBJECT",
        electron_num=5,
        completed_electron_num=0,
    )

    record_2 = models.Lattice(
        dispatch_id="dispatch_2",
        root_dispatch_id="dispatch_2",
        name="dispatch_2",
        status="NEW_OBJECT",
        electron_num=25,
        completed_electron_num=0,
    )

    record_3 = models.Lattice(
        dispatch_id="dispatch_3",
        root_dispatch_id="dispatch_2",
        name="dispatch_3",
        status="COMPLETED",
        electron_num=25,
        completed_electron_num=25,
    )

    with test_db.session() as session:
        session.add(record_1)
        session.add(record_2)
        session.add(record_3)
        session.commit()

    dispatch_controller = Result.meta_type

    with test_db.session() as session:
        results = dispatch_controller.get(
            session,
            fields=["dispatch_id"],
            equality_filters={},
            membership_filters={},
        )
        assert len(results) == 3

    with test_db.session() as session:
        results = dispatch_controller.get_toplevel_dispatches(
            session,
            fields=["dispatch_id"],
            equality_filters={},
            membership_filters={},
        )
        assert len(results) == 2

    with test_db.session() as session:
        results = dispatch_controller.get(
            session,
            fields=["dispatch_id"],
            equality_filters={},
            membership_filters={},
            sort_fields=["name"],
            reverse=False,
            max_items=1,
        )
        assert len(results) == 1
        assert results[0].dispatch_id == "dispatch_1"

    with test_db.session() as session:
        results = dispatch_controller.get(
            session,
            fields=["dispatch_id"],
            equality_filters={},
            membership_filters={},
            sort_fields=["name"],
            max_items=2,
            offset=1,
        )
        assert len(results) == 2
        assert results[0].dispatch_id == "dispatch_2"
