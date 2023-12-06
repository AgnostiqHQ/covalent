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
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import covalent as ct
from covalent._results_manager.result import Result
from covalent._workflow.lattice import Lattice as LatticeClass
from covalent._workflow.transportable_object import TransportableObject
from covalent.executor import LocalExecutor
from covalent_dispatcher._db.datastore import DataStore
from covalent_dispatcher._db.upsert import (
    ELECTRON_ERROR_FILENAME,
    ELECTRON_RESULTS_FILENAME,
    ELECTRON_STDERR_FILENAME,
    ELECTRON_STDOUT_FILENAME,
    _electron_data,
)

TEMP_RESULTS_DIR = os.environ.get("COVALENT_DATA_DIR") or ct.get_config("dispatcher.results_dir")
le = LocalExecutor(log_stdout="/tmp/stdout.log")


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


def test_upsert_electron_data_handles_missing_keys(test_db, result_1, mocker):
    """Test the _electron_data method handles missing node attributes"""

    mock_digest = MagicMock()
    mock_digest.algorithm = "md5"
    mock_digest.hexdigest = "123"
    mock_electron_row = MagicMock()
    mock_electron_row.id = 1
    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mock_store_file = mocker.patch(
        "covalent_dispatcher._db.upsert.local_store.store_file", return_value=(mock_digest, 2)
    )
    mocker.patch(
        "covalent_dispatcher._db.upsert.Electron.meta_type.create",
        return_value=mock_electron_row,
    )
    mocker.patch("covalent_dispatcher._db.write_result_to_db.update_electrons_data")
    mocker.patch(
        "covalent_dispatcher._db.write_result_to_db.update_lattice_completed_electron_num"
    )

    tg = result_1.lattice.transport_graph
    del tg._graph.nodes[0]["error"]
    del tg._graph.nodes[0]["stderr"]
    del tg._graph.nodes[0]["stdout"]
    del tg._graph.nodes[0]["output"]

    with test_db.session() as session:
        _electron_data(session, 1, result_1)

    node_path = Path(TEMP_RESULTS_DIR) / result_1.dispatch_id / "node_0"
    mock_store_file.assert_any_call(node_path, ELECTRON_ERROR_FILENAME, None)
    mock_store_file.assert_any_call(node_path, ELECTRON_STDOUT_FILENAME, None)
    mock_store_file.assert_any_call(node_path, ELECTRON_STDERR_FILENAME, None)
    mock_store_file.assert_any_call(
        node_path, ELECTRON_RESULTS_FILENAME, TransportableObject(None)
    )
