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

"""Unit tests for the module used to write the decomposed result object to the database."""

import json
from datetime import datetime as dt
from datetime import timezone

import pytest

import covalent as ct
from covalent._shared_files.defaults import (
    arg_prefix,
    attr_prefix,
    electron_dict_prefix,
    electron_list_prefix,
    generator_prefix,
    parameter_prefix,
    prefix_separator,
    sublattice_prefix,
    subscript_prefix,
)
from covalent_dispatcher._db.datastore import DataStore
from covalent_dispatcher._db.models import Electron, ElectronDependency, Job, Lattice
from covalent_dispatcher._db.write_result_to_db import (
    MissingElectronRecordError,
    MissingLatticeRecordError,
    get_electron_type,
    get_sublattice_electron_id,
    insert_electron_dependency_data,
    insert_electrons_data,
    insert_lattices_data,
    resolve_electron_id,
    transaction_upsert_electron_dependency_data,
    update_electrons_data,
    update_lattice_completed_electron_num,
    update_lattices_data,
)

STORAGE_TYPE = "file"
FUNCTION_FILENAME = "dispatch_source.pkl"
FUNCTION_STRING_FILENAME = "dispatch_source.py"
DOCSTRING_FILENAME = "dispatch_source_docstring.txt"
EXECUTOR_DATA_FILENAME = "executor_data.pkl"
WORKFLOW_EXECUTOR_DATA_FILENAME = "workflow_executor_data.pkl"
ERROR_FILENAME = "error.txt"
INPUTS_FILENAME = "inputs.pkl"
RESULTS_FILENAME = "results.pkl"
VALUE_FILENAME = "value.pkl"
STDOUT_FILENAME = "stdout.log"
STDERR_FILENAME = "stderr.log"
ERROR_FILENAME = "error.log"
TRANSPORT_GRAPH_FILENAME = "transport_graph.pkl"
HOOKS_FILENAME = "hooks.pkl"
RESULTS_DIR = "/tmp/results"


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


@pytest.fixture
def workflow_lattice():
    @ct.electron
    def task_1(x, y):
        return x * y

    @ct.electron
    def sublattice_task(z):
        return z

    @ct.electron
    @ct.lattice
    def task_2(z):
        return sublattice_task(z)

    @ct.lattice
    def workflow_1(a, b):
        res_1 = task_1(a, b)
        return task_2(res_1, b)

    workflow_1.build_graph(a=1, b=2)

    return workflow_1


def get_lattice_kwargs(
    dispatch_id="dispatch_1",
    electron_id=None,
    name="workflow_1",
    docstring_filename=DOCSTRING_FILENAME,
    status="RUNNING",
    electron_num=6,
    completed_electron_num=0,
    storage_type=STORAGE_TYPE,
    storage_path="results/dispatch_1/",
    function_filename=FUNCTION_FILENAME,
    function_string_filename=FUNCTION_STRING_FILENAME,
    executor="dask",
    executor_data=json.dumps({}),
    workflow_executor="dask",
    workflow_executor_data=json.dumps({}),
    error_filename=ERROR_FILENAME,
    inputs_filename=INPUTS_FILENAME,
    results_filename=RESULTS_FILENAME,
    hooks_filename=HOOKS_FILENAME,
    results_dir=RESULTS_DIR,
    root_dispatch_id="dispatch_1",
    created_at=None,
    updated_at=None,
    started_at=None,
    completed_at=None,
):
    """Create lattice kwargs."""

    return {
        "dispatch_id": dispatch_id,
        "electron_id": electron_id,
        "name": name,
        "docstring_filename": docstring_filename,
        "status": status,
        "electron_num": electron_num,
        "completed_electron_num": completed_electron_num,
        "storage_type": storage_type,
        "storage_path": storage_path,
        "function_filename": function_filename,
        "function_string_filename": function_string_filename,
        "executor": executor,
        "executor_data": executor_data,
        "workflow_executor": workflow_executor,
        "workflow_executor_data": workflow_executor_data,
        "error_filename": error_filename,
        "inputs_filename": inputs_filename,
        "results_filename": results_filename,
        "hooks_filename": hooks_filename,
        "results_dir": results_dir,
        "root_dispatch_id": root_dispatch_id,
        "created_at": created_at,
        "updated_at": updated_at,
        "started_at": started_at,
        "completed_at": completed_at,
    }


def get_electron_kwargs(
    parent_dispatch_id="dispatch_1",
    transport_graph_node_id=0,
    task_group_id=0,
    type=parameter_prefix.strip(prefix_separator),
    name=f"{parameter_prefix}0",
    status="NEW_OBJ",
    storage_type=STORAGE_TYPE,
    storage_path="results/dispatch_1/node_0/",
    function_filename=FUNCTION_STRING_FILENAME,
    function_string_filename=FUNCTION_STRING_FILENAME,
    executor="dask",
    executor_data=json.dumps({}),
    results_filename=RESULTS_FILENAME,
    value_filename=VALUE_FILENAME,
    stdout_filename=STDOUT_FILENAME,
    stderr_filename=STDERR_FILENAME,
    error_filename=ERROR_FILENAME,
    hooks_filename=HOOKS_FILENAME,
    job_id=1,
    qelectron_data_exists=False,
    created_at=None,
    updated_at=None,
    started_at=None,
    completed_at=None,
):
    """Create electron kwargs."""

    return {
        "parent_dispatch_id": parent_dispatch_id,
        "transport_graph_node_id": transport_graph_node_id,
        "task_group_id": task_group_id,
        "type": type,
        "name": name,
        "status": status,
        "storage_type": storage_type,
        "storage_path": storage_path,
        "function_filename": function_filename,
        "function_string_filename": function_string_filename,
        "executor": executor,
        "executor_data": executor_data,
        "results_filename": results_filename,
        "value_filename": value_filename,
        "stdout_filename": stdout_filename,
        "stderr_filename": stderr_filename,
        "error_filename": error_filename,
        "hooks_filename": hooks_filename,
        "job_id": job_id,
        "qelectron_data_exists": qelectron_data_exists,
        "created_at": created_at,
        "updated_at": updated_at,
        "started_at": started_at,
        "completed_at": completed_at,
    }


def test_update_lattice_completed_electron_num(test_db, mocker):
    """Test the function used to update the number of completed electrons for a lattice by 1."""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    cur_time = dt.now(timezone.utc)
    insert_lattices_data(
        **get_lattice_kwargs(created_at=cur_time, updated_at=cur_time, started_at=cur_time)
    )
    update_lattice_completed_electron_num(dispatch_id="dispatch_1")

    with test_db.session() as session:
        lat_record = session.query(Lattice).filter_by(dispatch_id="dispatch_1").first()
        assert lat_record.completed_electron_num == 1


def test_insert_lattices_data(test_db, mocker):
    """Test the function that inserts the lattices data in the DB."""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)

    timestamps = []
    for i in range(2):
        cur_time = dt.now(timezone.utc)
        timestamps.append(cur_time)
        lattice_args = get_lattice_kwargs(
            dispatch_id=f"dispatch_{i + 1}",
            name=f"workflow_{i + 1}",
            docstring_filename=f"docstring_{i + 1}.txt",
            storage_path=f"results/dispatch_{i + 1}/",
            executor="dask",
            workflow_executor="dask",
            created_at=cur_time,
            updated_at=cur_time,
            started_at=cur_time,
            root_dispatch_id=f"dispatch_{i + 1}",
        )
        insert_lattices_data(**lattice_args)

    with test_db.session() as session:
        rows = session.query(Lattice).all()

        for i, lattice in enumerate(rows):
            assert lattice.id == i + 1
            assert lattice.dispatch_id == f"dispatch_{i + 1}"
            assert lattice.electron_id is None
            assert lattice.name == f"workflow_{i + 1}"
            assert lattice.docstring_filename == f"docstring_{i + 1}.txt"
            assert lattice.status == "RUNNING"
            assert lattice.storage_type == STORAGE_TYPE
            assert lattice.storage_path == f"results/dispatch_{i + 1}/"
            assert lattice.function_filename == FUNCTION_FILENAME
            assert lattice.function_string_filename == FUNCTION_STRING_FILENAME
            assert lattice.executor == "dask"
            assert lattice.workflow_executor == "dask"
            assert lattice.error_filename == ERROR_FILENAME
            assert lattice.inputs_filename == INPUTS_FILENAME
            assert lattice.results_filename == RESULTS_FILENAME
            assert lattice.hooks_filename == HOOKS_FILENAME
            assert lattice.results_dir == RESULTS_DIR
            assert lattice.root_dispatch_id == f"dispatch_{i + 1}"
            assert (
                lattice.created_at.strftime("%m/%d/%Y, %H:%M:%S")
                == lattice.updated_at.strftime("%m/%d/%Y, %H:%M:%S")
                == lattice.started_at.strftime("%m/%d/%Y, %H:%M:%S")
                == timestamps[i].strftime("%m/%d/%Y, %H:%M:%S")
            )
            assert lattice.completed_at is None
            assert lattice.is_active
            assert isinstance(lattice.electron_num, int)
            assert isinstance(lattice.completed_electron_num, int)

    with test_db.session() as session:
        rows = session.query(Lattice).where(Lattice.dispatch_id == "dispatch_3").all()

        assert not rows


@pytest.mark.parametrize("cancel_requested", [True, False])
def test_insert_electrons_data(cancel_requested, test_db, mocker):
    """Test the function that inserts the electron data to the Electrons table."""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    cur_time = dt.now(timezone.utc)
    insert_lattices_data(
        **get_lattice_kwargs(created_at=cur_time, updated_at=cur_time, started_at=cur_time)
    )

    with test_db.session() as session:
        job_row = Job(cancel_requested=cancel_requested)
        session.add(job_row)
        session.flush()
        job_id = job_row.id

    electron_kwargs = {
        **get_electron_kwargs(
            job_id=job_id,
            created_at=cur_time,
            updated_at=cur_time,
        )
    }

    insert_electrons_data(**electron_kwargs)

    with test_db.session() as session:
        rows = session.query(Electron).all()
        assert len(rows) == 1

        for electron in rows:
            for key, value in electron_kwargs.items():
                if key == "parent_dispatch_id":
                    assert electron.parent_lattice_id == 1
                elif key in ["created_at", "updated_at"]:
                    assert getattr(electron, key).strftime("%m/%d/%Y, %H:%M:%S") == value.strftime(
                        "%m/%d/%Y, %H:%M:%S"
                    )
                elif key == "cancel_requested":
                    continue
                else:
                    assert getattr(electron, key) == value
            assert electron.is_active

        rows = session.query(Job).all()
        assert len(rows) == 1
        assert rows[0].cancel_requested == cancel_requested


def test_insert_electrons_data_missing_lattice_record(test_db, mocker):
    """Test the function that inserts the electron data to the Electrons table."""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)

    cur_time = dt.now(timezone.utc)
    electron_kwargs = {
        **get_electron_kwargs(
            created_at=cur_time,
            updated_at=cur_time,
        )
    }
    with pytest.raises(MissingLatticeRecordError):
        insert_electrons_data(**electron_kwargs)


def test_insert_electron_dependency_data(test_db, workflow_lattice, mocker):
    """Test the function that adds the electron dependencies of the lattice to the DB."""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    cur_time = dt.now(timezone.utc)
    insert_lattices_data(
        **get_lattice_kwargs(created_at=cur_time, updated_at=cur_time, started_at=cur_time)
    )

    electron_ids = []
    cur_time = dt.now(timezone.utc)
    for name, node_id in [
        ("task_1", 0),
        (":parameter:1", 1),
        (":parameter:2", 2),
        (":sublattice:task_2", 3),
        (":parameter:sublattice", 4),
        (":parameter:metadata", 5),
        (":parameter:2", 6),
        (":postprocess:", 7),
    ]:
        electron_kwargs = get_electron_kwargs(
            name=name,
            transport_graph_node_id=node_id,
            task_group_id=node_id,
            created_at=cur_time,
            updated_at=cur_time,
        )
        electron_ids.append(insert_electrons_data(**electron_kwargs))

    with test_db.session() as session:
        rows = session.query(Electron.id, Electron.transport_graph_node_id, Electron.name).all()

    insert_electron_dependency_data(dispatch_id="dispatch_1", lattice=workflow_lattice)

    with test_db.session() as session:
        rows = session.query(ElectronDependency).all()

        for electron_dependency in rows:
            if (
                electron_dependency.electron_id == 4
                and electron_dependency.parent_electron_id == 1
            ):
                # Note that `electron._build_sublattice_graph` is injected
                assert electron_dependency.edge_name == "arg[2]"
                assert electron_dependency.arg_index == 2
                assert electron_dependency.parameter_type == "arg"

            elif (
                electron_dependency.electron_id == 1
                and electron_dependency.parent_electron_id == 2
            ):
                assert electron_dependency.edge_name == "x"
                assert electron_dependency.arg_index == 0
                assert electron_dependency.parameter_type == "arg"

            elif (
                electron_dependency.electron_id == 1
                and electron_dependency.parent_electron_id == 3
            ):
                assert electron_dependency.edge_name == "y"
                assert electron_dependency.arg_index == 1
                assert electron_dependency.parameter_type == "arg"

            elif (
                electron_dependency.electron_id == 4
                and electron_dependency.parent_electron_id == 5
            ):
                assert electron_dependency.edge_name == "sub"
                assert electron_dependency.arg_index == 0
                assert electron_dependency.parameter_type == "arg"

            assert electron_dependency.is_active
            assert electron_dependency.updated_at is not None


def test_upsert_electron_dependency_data(test_db, workflow_lattice, mocker):
    """Test that upsert_electron_dependency_data is idempotent"""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    cur_time = dt.now(timezone.utc)
    insert_lattices_data(
        **get_lattice_kwargs(created_at=cur_time, updated_at=cur_time, started_at=cur_time)
    )

    electron_ids = []
    cur_time = dt.now(timezone.utc)
    for name, node_id in [
        ("task_1", 0),
        (":parameter:1", 1),
        (":parameter:2", 2),
        (":sublattice:task_2", 3),
        (":parameter:sublattice", 4),
        (":parameter:metadata", 5),
        (":parameter:2", 6),
        (":postprocess:", 7),
    ]:
        electron_kwargs = get_electron_kwargs(
            name=name,
            transport_graph_node_id=node_id,
            task_group_id=node_id,
            created_at=cur_time,
            updated_at=cur_time,
        )
        electron_ids.append(insert_electrons_data(**electron_kwargs))

    mock_insert = mocker.patch(
        "covalent_dispatcher._db.write_result_to_db.transaction_insert_electron_dependency_data"
    )

    with test_db.session() as session:
        transaction_upsert_electron_dependency_data(
            session=session, dispatch_id="dispatch_1", lattice=workflow_lattice
        )

        mock_insert.assert_called_once_with(
            session=session, dispatch_id="dispatch_1", lattice=workflow_lattice
        )


def test_upsert_electron_dependency_data_idempotent(test_db, workflow_lattice, mocker):
    """Test that upsert_electron_dependency_data is idempotent"""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    cur_time = dt.now(timezone.utc)
    insert_lattices_data(
        **get_lattice_kwargs(created_at=cur_time, updated_at=cur_time, started_at=cur_time)
    )

    electron_ids = []
    cur_time = dt.now(timezone.utc)
    for name, node_id in [
        ("task_1", 0),
        (":parameter:1", 1),
        (":parameter:2", 2),
        (":sublattice:task_2", 3),
        (":parameter:sublattice", 4),
        (":parameter:metadata", 5),
        (":parameter:2", 6),
        (":postprocess:", 7),
    ]:
        electron_kwargs = get_electron_kwargs(
            name=name,
            transport_graph_node_id=node_id,
            task_group_id=node_id,
            created_at=cur_time,
            updated_at=cur_time,
        )
        electron_ids.append(insert_electrons_data(**electron_kwargs))

    insert_electron_dependency_data(dispatch_id="dispatch_1", lattice=workflow_lattice)

    mock_insert = mocker.patch(
        "covalent_dispatcher._db.write_result_to_db.insert_electron_dependency_data"
    )

    with test_db.session() as session:
        transaction_upsert_electron_dependency_data(
            session=session, dispatch_id="dispatch_1", lattice=workflow_lattice
        )

    mock_insert.assert_not_called()


def test_update_lattices_data(test_db, mocker):
    """Test the function that updates the lattice data."""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    cur_time = dt.now(timezone.utc)
    with pytest.raises(MissingLatticeRecordError):
        update_lattices_data(
            dispatch_id="dispatch_1",
            status="COMPLETED",
            started_at=cur_time,
            updated_at=cur_time,
            completed_at=cur_time,
        )

    insert_lattices_data(
        **get_lattice_kwargs(created_at=cur_time, updated_at=cur_time, started_at=cur_time)
    )
    update_lattices_data(
        dispatch_id="dispatch_1",
        status="COMPLETED",
        completed_electron_num=5,
        updated_at=cur_time,
        completed_at=cur_time,
    )

    with test_db.session() as session:
        rows = session.query(Lattice).all()

        for lattice in rows:
            assert lattice.status == "COMPLETED"
            assert (
                lattice.updated_at.strftime("%m/%d/%Y, %H:%M:%S")
                == lattice.completed_at.strftime("%m/%d/%Y, %H:%M:%S")
                == cur_time.strftime("%m/%d/%Y, %H:%M:%S")
                == lattice.started_at.strftime("%m/%d/%Y, %H:%M:%S")
            )
            assert lattice.id == 1
            assert lattice.completed_electron_num == 5


def test_update_electrons_data(test_db, mocker):
    """Test the function that updates the data in the Electrons table."""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    insert_lattices_data(
        **get_lattice_kwargs(
            created_at=dt.now(timezone.utc),
            updated_at=dt.now(timezone.utc),
            started_at=dt.now(timezone.utc),
        ),
    )

    with pytest.raises(MissingElectronRecordError):
        update_electrons_data(
            parent_dispatch_id="dispatch_1",
            transport_graph_node_id=0,
            name="task",
            status="RUNNING",
            started_at=dt.now(timezone.utc),
            updated_at=dt.now(timezone.utc),
            completed_at=None,
            qelectron_data_exists=False,
        )

    insert_electrons_data(
        **get_electron_kwargs(
            created_at=dt.now(timezone.utc),
            updated_at=dt.now(timezone.utc),
        ),
    )
    cur_time = dt.now(timezone.utc)
    update_electrons_data(
        parent_dispatch_id="dispatch_1",
        transport_graph_node_id=0,
        name="task",
        status="RUNNING",
        started_at=cur_time,
        updated_at=cur_time,
        completed_at=None,
        qelectron_data_exists=False,
    )

    with test_db.session() as session:
        rows = session.query(Electron).all()

        for electron in rows:
            assert electron.status == "RUNNING"
            assert (
                electron.started_at.strftime("%m/%d/%Y, %H:%M:%S")
                == electron.updated_at.strftime("%m/%d/%Y, %H:%M:%S")
                == cur_time.strftime("%m/%d/%Y, %H:%M:%S")
            )


@pytest.mark.parametrize(
    "node_name,electron_type",
    [
        (f"{parameter_prefix}0", parameter_prefix.strip(prefix_separator)),
        (f"{arg_prefix}1", arg_prefix.strip(prefix_separator)),
        (f"{attr_prefix}2", attr_prefix.strip(prefix_separator)),
        (f"{electron_dict_prefix}3", electron_dict_prefix.strip(prefix_separator)),
        (f"{electron_list_prefix}4", electron_list_prefix.strip(prefix_separator)),
        (f"{generator_prefix}5", generator_prefix.strip(prefix_separator)),
        (f"{sublattice_prefix}sometask", sublattice_prefix.strip(prefix_separator)),
        (f"{subscript_prefix}6", subscript_prefix.strip(prefix_separator)),
        ("regular_task", "function"),
    ],
)
def test_get_electron_type(node_name, electron_type):
    """Test that given an electron node, the correct electron type is returned."""

    assert get_electron_type(node_name) == electron_type


def test_write_sublattice_electron_id(test_db, mocker):
    """Test that the sublattice electron id is written in the lattice record."""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    cur_time = dt.now(timezone.utc)
    insert_lattices_data(
        **get_lattice_kwargs(created_at=cur_time, updated_at=cur_time, started_at=cur_time)
    )

    # Create electron records.
    electron_ids = []
    cur_time = dt.now(timezone.utc)
    for name, node_id in [
        ("task_1", 0),
        (":parameter:1", 1),
        (":parameter:2", 2),
        (":sublattice:task_2", 3),  # Sublattice node id
        (":parameter:2", 4),
    ]:
        electron_kwargs = get_electron_kwargs(
            name=name,
            transport_graph_node_id=node_id,
            task_group_id=node_id,
            created_at=cur_time,
            updated_at=cur_time,
        )
        electron_ids.append(insert_electrons_data(**electron_kwargs))

    # Create sublattice record.
    cur_time = dt.now(timezone.utc)
    sub_electron_id = get_sublattice_electron_id(
        parent_dispatch_id="dispatch_1", sublattice_node_id=3
    )
    insert_lattices_data(
        **get_lattice_kwargs(
            dispatch_id="dispatch_2",
            electron_id=sub_electron_id,
            created_at=cur_time,
            updated_at=cur_time,
            started_at=cur_time,
        ),
    )

    # Assert that the electron id has indeed been written.
    with test_db.session() as session:
        rows = session.query(Lattice).all()

        assert rows[0].dispatch_id == "dispatch_1"
        assert rows[0].electron_id is None
        assert rows[1].dispatch_id == "dispatch_2"


def test_resolve_electron_id(test_db, mocker):
    """Test looking up dispatch_id and node_id corresponding to an electron_id"""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    cur_time = dt.now(timezone.utc)
    insert_lattices_data(
        **get_lattice_kwargs(created_at=cur_time, updated_at=cur_time, started_at=cur_time)
    )

    # Create electron records.
    electron_ids = []
    cur_time = dt.now(timezone.utc)
    for name, node_id in [
        ("task_1", 0),
        (":parameter:1", 1),
        (":parameter:2", 2),
        (":sublattice:task_2", 3),  # Sublattice node id
        (":parameter:2", 4),
    ]:
        electron_kwargs = get_electron_kwargs(
            name=name,
            transport_graph_node_id=node_id,
            task_group_id=node_id,
            created_at=cur_time,
            updated_at=cur_time,
        )
        eid = insert_electrons_data(**electron_kwargs)
        electron_ids.append(eid)

    dispatch_id, node_id = resolve_electron_id(electron_ids[3])
    assert dispatch_id == "dispatch_1"
    assert node_id == 3
