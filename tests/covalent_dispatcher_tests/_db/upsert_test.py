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
from pathlib import Path

import pytest

import covalent as ct
from covalent._results_manager.result import Result
from covalent._workflow.lattice import Lattice as LatticeClass
from covalent.executor import LocalExecutor
from covalent_dispatcher._db.datastore import DataStore
from covalent_dispatcher._db.upsert import (
    ELECTRON_ERROR_FILENAME,
    ELECTRON_RESULTS_FILENAME,
    ELECTRON_STDERR_FILENAME,
    ELECTRON_STDOUT_FILENAME,
    LATTICE_FUNCTION_STRING_FILENAME,
    electron_data,
    lattice_data,
)

TEMP_RESULTS_DIR = "/tmp/results"
le = LocalExecutor(log_stdout="/tmp/stdout.log")


@pytest.fixture
def result_1():
    @ct.electron(executor="dask")
    def task_1(x, y):
        return x * y

    @ct.electron(executor=le)
    def task_2(x, y):
        return x + y

    @ct.lattice(executor=le, workflow_executor=le, results_dir=TEMP_RESULTS_DIR)
    def workflow_1(a, b):
        """Docstring"""
        res_1 = task_1(a, b)
        return task_2(res_1, b)

    Path(f"{TEMP_RESULTS_DIR}/dispatch_1").mkdir(parents=True, exist_ok=True)
    workflow_1.build_graph(a=1, b=2)
    received_lattice = LatticeClass.deserialize_from_json(workflow_1.serialize_to_json())
    result = Result(
        lattice=received_lattice, results_dir=TEMP_RESULTS_DIR, dispatch_id="dispatch_1"
    )
    result.lattice.metadata["results_dir"] = TEMP_RESULTS_DIR
    result._initialize_nodes()
    return result


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def test_upsert_electron_data_handles_missing_keys(test_db, result_1, mocker):
    """Test the electron_data method handles missing node attributes"""

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mock_store_file = mocker.patch("covalent_dispatcher._db.upsert.store_file")
    mocker.patch("covalent_dispatcher._db.upsert.txn_insert_electrons_data")
    mocker.patch("covalent_dispatcher._db.write_result_to_db.update_electrons_data")
    mocker.patch(
        "covalent_dispatcher._db.write_result_to_db.update_lattice_completed_electron_num"
    )

    tg = result_1.lattice.transport_graph
    del tg._graph.nodes[0]["error"]
    del tg._graph.nodes[0]["stderr"]
    del tg._graph.nodes[0]["stdout"]
    del tg._graph.nodes[0]["output"]

    electron_data(result_1)

    node_path = Path(TEMP_RESULTS_DIR) / result_1.dispatch_id / "node_0"
    mock_store_file.assert_any_call(node_path, ELECTRON_ERROR_FILENAME, None)
    mock_store_file.assert_any_call(node_path, ELECTRON_STDOUT_FILENAME, None)
    mock_store_file.assert_any_call(node_path, ELECTRON_STDERR_FILENAME, None)
    mock_store_file.assert_any_call(node_path, ELECTRON_RESULTS_FILENAME, None)


def test_public_lattice_data(test_db, result_1, mocker):
    """Test the lattice_data public method"""
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)

    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mock_store_file = mocker.patch("covalent_dispatcher._db.upsert.store_file")
    mock_insert = mocker.patch("covalent_dispatcher._db.upsert.txn_insert_lattices_data")
    mocker.patch("covalent_dispatcher._db.upsert.txn_update_lattices_data")

    lattice_path = Path(TEMP_RESULTS_DIR) / result_1.dispatch_id

    lattice_data(result_1)
    mock_store_file.assert_any_call(
        lattice_path, LATTICE_FUNCTION_STRING_FILENAME, result_1.lattice.workflow_function_string
    )

    del result_1.lattice.__dict__["workflow_function_string"]
    mock_store_file.reset_mock()
    lattice_data(result_1)
    mock_store_file.assert_any_call(lattice_path, LATTICE_FUNCTION_STRING_FILENAME, None)
