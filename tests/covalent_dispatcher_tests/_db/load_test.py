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

"""Unit tests for the module used to load transport graphs from the DB."""

from datetime import datetime as dt
from datetime import timezone

import pytest

import covalent as ct
from covalent._shared_files.defaults import parameter_prefix, prefix_separator
from covalent_dispatcher._db.datastore import DataStore
from covalent_dispatcher._db.load import task_job_map
from covalent_dispatcher._db.write_result_to_db import (
    get_electron_type,
    insert_electron_dependency_data,
    insert_electrons_data,
    insert_lattices_data,
)

STORAGE_TYPE = "local"
FUNCTION_FILENAME = "dispatch_source.pkl"
FUNCTION_STRING_FILENAME = "dispatch_source.py"
DOCSTRING_FILENAME = "dispatch_source_docstring.txt"
EXECUTOR_DATA_FILENAME = "executor_data.pkl"
WORKFLOW_EXECUTOR_DATA_FILENAME = "workflow_executor_data.pkl"
ERROR_FILENAME = "error.txt"
INPUTS_FILENAME = "inputs.pkl"
NAMED_ARGS_FILENAME = "named_args.pkl"
NAMED_KWARGS_FILENAME = "named_kwargs.pkl"
RESULTS_FILENAME = "results.pkl"
VALUE_FILENAME = "value.pkl"
STDOUT_FILENAME = "stdout.log"
STDERR_FILENAME = "stderr.log"
ERROR_FILENAME = "error.log"
TRANSPORT_GRAPH_FILENAME = "transport_graph.pkl"
DEPS_FILENAME = "deps.pkl"
CALL_BEFORE_FILENAME = "call_before.pkl"
CALL_AFTER_FILENAME = "call_after.pkl"
COVA_IMPORTS_FILENAME = "cova_imports.pkl"
LATTICE_IMPORTS_FILENAME = "lattice_imports.pkl"
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
    executor_data_filename=EXECUTOR_DATA_FILENAME,
    workflow_executor="dask",
    workflow_executor_data_filename=WORKFLOW_EXECUTOR_DATA_FILENAME,
    error_filename=ERROR_FILENAME,
    inputs_filename=INPUTS_FILENAME,
    named_args_filename=NAMED_ARGS_FILENAME,
    named_kwargs_filename=NAMED_KWARGS_FILENAME,
    results_filename=RESULTS_FILENAME,
    transport_graph_filename=TRANSPORT_GRAPH_FILENAME,
    deps_filename=DEPS_FILENAME,
    call_before_filename=CALL_BEFORE_FILENAME,
    call_after_filename=CALL_AFTER_FILENAME,
    cova_imports_filename=COVA_IMPORTS_FILENAME,
    lattice_imports_filename=LATTICE_IMPORTS_FILENAME,
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
        "executor_data_filename": executor_data_filename,
        "workflow_executor": workflow_executor,
        "workflow_executor_data_filename": workflow_executor_data_filename,
        "error_filename": error_filename,
        "inputs_filename": inputs_filename,
        "named_args_filename": named_args_filename,
        "named_kwargs_filename": named_kwargs_filename,
        "results_filename": results_filename,
        "transport_graph_filename": transport_graph_filename,
        "deps_filename": deps_filename,
        "call_before_filename": call_before_filename,
        "call_after_filename": call_after_filename,
        "cova_imports_filename": cova_imports_filename,
        "lattice_imports_filename": lattice_imports_filename,
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
    type=parameter_prefix.strip(prefix_separator),
    name=f"{parameter_prefix}0",
    status="NEW_OBJ",
    storage_type=STORAGE_TYPE,
    storage_path="results/dispatch_1/node_0/",
    function_filename=FUNCTION_STRING_FILENAME,
    function_string_filename=FUNCTION_STRING_FILENAME,
    executor="dask",
    executor_data_filename=EXECUTOR_DATA_FILENAME,
    results_filename=RESULTS_FILENAME,
    value_filename=VALUE_FILENAME,
    stdout_filename=STDOUT_FILENAME,
    stderr_filename=STDERR_FILENAME,
    error_filename=ERROR_FILENAME,
    deps_filename=DEPS_FILENAME,
    cancel_requested=False,
    call_before_filename=CALL_BEFORE_FILENAME,
    call_after_filename=CALL_AFTER_FILENAME,
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
        "executor": executor,
        "executor_data_filename": executor_data_filename,
        "results_filename": results_filename,
        "value_filename": value_filename,
        "stdout_filename": stdout_filename,
        "stderr_filename": stderr_filename,
        "error_filename": error_filename,
        "deps_filename": deps_filename,
        "call_before_filename": call_before_filename,
        "call_after_filename": call_after_filename,
        "cancel_requested": cancel_requested,
        "created_at": created_at,
        "updated_at": updated_at,
        "started_at": started_at,
        "completed_at": completed_at,
    }


def test_task_job_map(test_db, workflow_lattice, mocker):

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.load.workflow_db", test_db)
    lattice_kwargs = get_lattice_kwargs()
    insert_lattices_data(**lattice_kwargs)
    cur_time = dt.now(timezone.utc)
    for (name, node_id) in [
        ("task_1", 0),
        (":parameter:1", 1),
        (":parameter:2", 2),
        (":sublattice:task_2", 3),
        (":parameter:2", 4),
    ]:
        electron_kwargs = get_electron_kwargs(
            name=name,
            type=get_electron_type(name),
            transport_graph_node_id=node_id,
            created_at=cur_time,
            updated_at=cur_time,
        )
        insert_electrons_data(**electron_kwargs)

    insert_electron_dependency_data("dispatch_1", workflow_lattice)

    job_map = task_job_map("dispatch_1")

    for i in range(5):
        assert job_map[i] == i + 1
