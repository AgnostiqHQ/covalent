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

"""Unit tests for the module used to write the decomposed result object to the database."""

from datetime import datetime as dt

import pytest
from sqlalchemy.orm import Session

import covalent as ct
from covalent._data_store.datastore import DataStore
from covalent._data_store.models import Electron, ElectronDependency, Lattice
from covalent._results_manager.write_result_to_db import (
    MissingElectronRecordError,
    MissingLatticeRecordError,
    get_electron_type,
    insert_electron_dependency_data,
    insert_electrons_data,
    insert_lattices_data,
    update_electrons_data,
    update_lattices_data,
)
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

STORAGE_TYPE = "local"
FUNCTION_FILENAME = "dispatch_source.pkl"
FUNCTION_STRING_FILENAME = "dispatch_source.py"
EXECUTOR_FILENAME = "executor.pkl"
ERROR_FILENAME = "error.txt"
INPUTS_FILENAME = "inputs.pkl"
RESULTS_FILENAME = "result.pkl"
VALUE_FILENAME = "value.pkl"
STDOUT_FILENAME = "stdout.log"
STDERR_FILENAME = "stderr.log"
INFO_FILENAME = "info.log"


@pytest.fixture
def db():
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

    return workflow_1


def get_lattice_kwargs(
    dispatch_id="dispatch_1",
    name="workflow_1",
    status="RUNNING",
    storage_type=STORAGE_TYPE,
    storage_path="results/dispatch_1/",
    function_filename=FUNCTION_FILENAME,
    function_string_filename=FUNCTION_STRING_FILENAME,
    executor_filename=EXECUTOR_FILENAME,
    error_filename=ERROR_FILENAME,
    inputs_filename=INPUTS_FILENAME,
    results_filename=RESULTS_FILENAME,
    created_at=None,
    updated_at=None,
    started_at=None,
    completed_at=None,
):
    """Create lattice kwargs."""

    return {
        "dispatch_id": dispatch_id,
        "name": name,
        "status": status,
        "storage_type": storage_type,
        "storage_path": storage_path,
        "function_filename": function_filename,
        "function_string_filename": function_string_filename,
        "executor_filename": executor_filename,
        "error_filename": error_filename,
        "inputs_filename": inputs_filename,
        "results_filename": results_filename,
        "created_at": created_at,
        "updated_at": updated_at,
        "started_at": started_at,
        "completed_at": completed_at,
    }


def get_electron_kwargs(
    parent_dispatch_id="dispatch_1",
    transport_graph_node_id=0,
    type=parameter_prefix.strip(prefix_separator),
    name=f"{parameter_prefix}0",
    status="NEW_OBJ",
    storage_type=STORAGE_TYPE,
    storage_path="results/dispatch_1/node_0/",
    function_filename=FUNCTION_STRING_FILENAME,
    function_string_filename=FUNCTION_STRING_FILENAME,
    executor_filename=EXECUTOR_FILENAME,
    results_filename=RESULTS_FILENAME,
    value_filename=VALUE_FILENAME,
    attribute_name=None,
    key=None,
    stdout_filename=STDOUT_FILENAME,
    stderr_filename=STDERR_FILENAME,
    info_filename=INFO_FILENAME,
    created_at=None,
    updated_at=None,
    started_at=None,
    completed_at=None,
):
    """Create electron kwargs."""

    return {
        "parent_dispatch_id": parent_dispatch_id,
        "transport_graph_node_id": transport_graph_node_id,
        "type": type,
        "name": name,
        "status": status,
        "storage_type": storage_type,
        "storage_path": storage_path,
        "function_filename": function_filename,
        "function_string_filename": function_string_filename,
        "executor_filename": executor_filename,
        "results_filename": results_filename,
        "value_filename": value_filename,
        "attribute_name": attribute_name,
        "key": key,
        "stdout_filename": stdout_filename,
        "stderr_filename": stderr_filename,
        "info_filename": info_filename,
        "created_at": created_at,
        "updated_at": updated_at,
        "started_at": started_at,
        "completed_at": completed_at,
    }


def test_insert_lattices_data(db):
    """Test the function that inserts the lattices data in the DB."""

    lattice_ids = []
    timestamps = []

    for i in range(2):
        cur_time = dt.now()
        timestamps.append(cur_time)
        lattice_args = get_lattice_kwargs(
            dispatch_id=f"dispatch_{i + 1}",
            name=f"workflow_{i + 1}",
            storage_path=f"results/dispatch_{i+1}/",
            created_at=cur_time,
            updated_at=cur_time,
            started_at=cur_time,
        )
        lattice_id = insert_lattices_data(db=db, **lattice_args)
        lattice_ids.append(lattice_id)

    assert lattice_ids == [1, 2]

    with Session(db.engine) as session:
        rows = session.query(Lattice).all()

    for i, lattice in enumerate(rows):
        assert lattice.id == i + 1
        assert lattice.dispatch_id == f"dispatch_{i + 1}"
        assert lattice.name == f"workflow_{i + 1}"
        assert lattice.status == "RUNNING"
        assert lattice.storage_type == STORAGE_TYPE
        assert lattice.storage_path == f"results/dispatch_{i+1}/"
        assert lattice.function_filename == FUNCTION_FILENAME
        assert lattice.function_string_filename == FUNCTION_STRING_FILENAME
        assert lattice.executor_filename == EXECUTOR_FILENAME
        assert lattice.error_filename == ERROR_FILENAME
        assert lattice.inputs_filename == INPUTS_FILENAME
        assert lattice.results_filename == RESULTS_FILENAME
        assert lattice.created_at == lattice.updated_at == lattice.started_at == timestamps[i]
        assert lattice.completed_at is None

        with Session(db.engine) as session:
            rows = session.query(Lattice).where(Lattice.dispatch_id == "dispatch_3").all()

        assert not rows


def test_insert_electrons_data(db):
    """Test the function that inserts the electron data to the Electrons table."""

    cur_time = dt.now()
    insert_lattices_data(
        db=db, **get_lattice_kwargs(created_at=cur_time, updated_at=cur_time, started_at=cur_time)
    )

    electron_kwargs = {
        **get_electron_kwargs(
            created_at=cur_time,
            updated_at=cur_time,
        )
    }

    electron_id = insert_electrons_data(db=db, **electron_kwargs)
    assert electron_id == 1

    with Session(db.engine) as session:
        rows = session.query(Electron).all()

    assert len(rows) == 1

    for electron in rows:
        for key, value in electron_kwargs.items():
            if key == "parent_dispatch_id":
                assert electron.parent_lattice_id == 1
            else:
                assert getattr(electron, key) == value

    electron_id = insert_electrons_data(db=db, **electron_kwargs)
    assert electron_id == 2


def test_insert_electrons_data_missing_lattice_record(db):
    """Test the function that inserts the electron data to the Electrons table."""

    cur_time = dt.now()
    electron_kwargs = {
        **get_electron_kwargs(
            created_at=cur_time,
            updated_at=cur_time,
        )
    }
    with pytest.raises(MissingLatticeRecordError):
        insert_electrons_data(db=db, **electron_kwargs)


def test_insert_electron_dependency_data(db):
    """Test the function that adds the electron dependencies of the lattice to the DB."""

    cur_time = dt.now()
    insert_lattices_data(
        db=db, **get_lattice_kwargs(created_at=cur_time, updated_at=cur_time, started_at=cur_time)
    )
    insert_lattices_data(
        db=db, **get_lattice_kwargs(created_at=cur_time, updated_at=cur_time, started_at=cur_time)
    )

    electron_ids = []
    cur_time = dt.now()
    for (name, node_id) in [
        ("task_1", 0),
        (":parameter:1", 1),
        (":parameter:2", 2),
        (":sublattice:task_2", 3),
        (":parameter:2", 4),
    ]:
        electron_kwargs = get_electron_kwargs(
            name=name,
            transport_graph_node_id=node_id,
            created_at=cur_time,
            updated_at=cur_time,
        )
        print(electron_kwargs)
        electron_ids.append(insert_electrons_data(db=db, **electron_kwargs))

    dependency_ids = insert_electron_dependency_data(
        db=db, dispatch_id="dispatch_1", lattice=workflow_lattice
    )

    assert dependency_ids == [1, 2, 3, 4]

    with Session(db.engine) as session:
        rows = session.query(ElectronDependency).all()

    actual_electron_dependencies = {
        {
            "edge_name": electron_dependency.edge_name,
            "parameter_index": electron_dependency.parameter_index,
            "parameter_type": electron_dependency.parameter_type,
            "parent_electron_id": electron_dependency.parent_electron_id,
            "electron_id": electron_dependency.electron_id,
        }
        for electron_dependency in rows
    }

    assert set(actual_electron_dependencies) == {
        {
            "edge_name": "arg[0]",
            "parameter_index": 0,
            "parameter_type": "arg",
            "parent_electron_id": 1,  # 'source': 0,
            "electron_id": 4,  # 'target': 3
        },
        {
            "edge_name": "x",
            "partameter_index": 0,
            "parameter_type": "arg",
            "parent_electron_id": 2,  # 'source': 1,
            "electron_id": 1,  # 'target': 0
        },
        {
            "edge_name": "y",
            "parameter_index": 0,
            "parameter_type": "arg",
            "parent_electron_id": 3,  # 'source': 2,
            "electron_id": 1,  # 'target': 0
        },
        {
            "edge_name": "arg[1]",
            "parameter_index": 0,
            "parameter_type": "arg",
            "parent_electron_id": 5,  # 'source': 4,
            "electron_id": 4,  # 'target': 3
        },
    }


def test_update_lattices_data(db):
    """Test the function that updates the lattice data."""

    cur_time = dt.now()
    with pytest.raises(MissingLatticeRecordError):
        update_lattices_data(
            db=db,
            dispatch_id="dispatch_1",
            status="COMPLETED",
            updated_at=cur_time,
            completed_at=cur_time,
        )

    insert_lattices_data(
        db=db, **get_lattice_kwargs(created_at=cur_time, updated_at=cur_time, started_at=cur_time)
    )
    update_lattices_data(
        db=db,
        dispatch_id="dispatch_1",
        status="COMPLETED",
        updated_at=cur_time,
        completed_at=cur_time,
    )

    with Session(db.engine) as session:
        rows = session.query(Lattice).all()

    for lattice in rows:
        assert lattice.status == "COMPLETED"
        assert lattice.updated_at == lattice.completed_at == cur_time
        assert lattice.id == 1


def test_update_electrons_data(db):
    """Test the function that updates the data in the Electrons table."""

    insert_lattices_data(
        db=db, **get_lattice_kwargs(created_at=dt.now(), updated_at=dt.now(), started_at=dt.now())
    )

    with pytest.raises(MissingElectronRecordError):
        update_electrons_data(
            db=db,
            parent_dispatch_id="dispatch_1",
            transport_graph_node_id=0,
            status="RUNNING",
            started_at=dt.now(),
            updated_at=dt.now(),
            completed_at=None,
        )

    insert_electrons_data(db=db, **get_electron_kwargs(created_at=dt.now(), updated_at=dt.now()))
    cur_time = dt.now()
    update_electrons_data(
        db=db,
        parent_dispatch_id="dispatch_1",
        transport_graph_node_id=0,
        status="RUNNING",
        started_at=cur_time,
        updated_at=cur_time,
        completed_at=None,
    )

    with Session(db.engine) as session:
        rows = session.query(Electron).all()

    for electron in rows:
        assert electron.status == "RUNNING"
        assert electron.started_at == electron.updated_at == cur_time


def test_are_electron_dependencies_added():
    pass


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

    node = {"name": node_name}

    assert get_electron_type(node) == electron_type
