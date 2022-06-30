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

from covalent._data_store.datastore import DataStore
from covalent._data_store.models import Lattice
from covalent._results_manager.write_result_to_db import get_electron_type, insert_lattices_data
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


@pytest.fixture
def db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def test_insert_lattices_data(db):
    """Test the function that inserts the lattices data in the DB."""

    lattice_ids = []
    timestamps = []

    for i in range(2):
        cur_time = dt.now()
        timestamps.append(cur_time)
        lattice_id = insert_lattices_data(
            db=db,
            dispatch_id=f"dispatch_{i + 1}",
            name=f"workflow_{i + 1}",
            status="RUNNING",
            storage_type=STORAGE_TYPE,
            storage_path=f"results/dispatch_{i+1}/",
            function_filename=FUNCTION_FILENAME,
            function_string_filename=FUNCTION_STRING_FILENAME,
            executor_filename=EXECUTOR_FILENAME,
            error_filename=ERROR_FILENAME,
            inputs_filename=INPUTS_FILENAME,
            results_filename=RESULTS_FILENAME,
            created_at=cur_time,
            updated_at=cur_time,
            started_at=cur_time,
            completed_at=cur_time,
        )
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
        assert (
            lattice.created_at
            == lattice.updated_at
            == lattice.started_at
            == lattice.completed_at
            == timestamps[i]
        )

        with Session(db.engine) as session:
            rows = session.query(Lattice).where(Lattice.dispatch_id == "dispatch_3").all()

        assert not rows


def test_insert_electrons_data():
    pass


def test_insert_electron_dependency_data():
    pass


def test_update_lattices_data():
    pass


def test_update_electrons_data():
    pass


def test_get_electron_dependencies():
    pass


def test_sublattice_electron_id():
    pass


def test_are_electron_dependencies_added():
    pass


def test_is_lattice_added():
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
