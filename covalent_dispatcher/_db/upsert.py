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
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.config import get_config

from . import models
from .datastore import workflow_db
from .jobdb import txn_get_job_record
from .write_result_to_db import (
    get_electron_type,
    store_file,
    txn_insert_electrons_data,
    txn_insert_lattices_data,
    txn_update_lattices_data,
    txn_upsert_electron_dependency_data,
    update_electrons_data,
    update_lattice_completed_electron_num,
)

app_log = logger.app_log

ELECTRON_FUNCTION_FILENAME = "function.pkl"
ELECTRON_FUNCTION_STRING_FILENAME = "function_string.txt"
ELECTRON_VALUE_FILENAME = "value.pkl"
ELECTRON_EXECUTOR_DATA_FILENAME = "executor_data.pkl"
ELECTRON_STDOUT_FILENAME = "stdout.log"
ELECTRON_STDERR_FILENAME = "stderr.log"
ELECTRON_ERROR_FILENAME = "error.log"
ELECTRON_RESULTS_FILENAME = "results.pkl"
ELECTRON_DEPS_FILENAME = "deps.pkl"
ELECTRON_CALL_BEFORE_FILENAME = "call_before.pkl"
ELECTRON_CALL_AFTER_FILENAME = "call_after.pkl"
ELECTRON_STORAGE_TYPE = "local"
LATTICE_FUNCTION_FILENAME = "function.pkl"
LATTICE_FUNCTION_STRING_FILENAME = "function_string.txt"
LATTICE_DOCSTRING_FILENAME = "function_docstring.txt"
LATTICE_EXECUTOR_DATA_FILENAME = "executor_data.pkl"
LATTICE_WORKFLOW_EXECUTOR_DATA_FILENAME = "workflow_executor_data.pkl"
LATTICE_ERROR_FILENAME = "error.log"
LATTICE_INPUTS_FILENAME = "inputs.pkl"
LATTICE_NAMED_ARGS_FILENAME = "named_args.pkl"
LATTICE_NAMED_KWARGS_FILENAME = "named_kwargs.pkl"
LATTICE_RESULTS_FILENAME = "results.pkl"
LATTICE_TRANSPORT_GRAPH_FILENAME = "transport_graph.pkl"
LATTICE_DEPS_FILENAME = "deps.pkl"
LATTICE_CALL_BEFORE_FILENAME = "call_before.pkl"
LATTICE_CALL_AFTER_FILENAME = "call_after.pkl"
LATTICE_COVA_IMPORTS_FILENAME = "cova_imports.pkl"
LATTICE_LATTICE_IMPORTS_FILENAME = "lattice_imports.pkl"
LATTICE_STORAGE_TYPE = "local"


def _lattice_data(session: Session, result: Result, electron_id: int = None):
    lattice_exists = (
        session.query(models.Lattice)
        .where(models.Lattice.dispatch_id == result.dispatch_id)
        .first()
        is not None
    )

    try:
        workflow_func_string = result.lattice.workflow_function_string
    except AttributeError:
        workflow_func_string = None

    # Store all lattice info that belongs in filenames in the results directory
    results_dir = os.environ.get("COVALENT_DATA_DIR") or get_config("dispatcher.results_dir")
    data_storage_path = os.path.join(results_dir, result.dispatch_id)
    for filename, data in [
        (LATTICE_FUNCTION_FILENAME, result.lattice.workflow_function),
        (LATTICE_FUNCTION_STRING_FILENAME, workflow_func_string),
        (LATTICE_DOCSTRING_FILENAME, result.lattice.__doc__),
        (LATTICE_EXECUTOR_DATA_FILENAME, result.lattice.metadata["executor_data"]),
        (
            LATTICE_WORKFLOW_EXECUTOR_DATA_FILENAME,
            result.lattice.metadata["workflow_executor_data"],
        ),
        (LATTICE_ERROR_FILENAME, result.error),
        (LATTICE_INPUTS_FILENAME, result.inputs),
        (LATTICE_NAMED_ARGS_FILENAME, result.lattice.named_args),
        (LATTICE_NAMED_KWARGS_FILENAME, result.lattice.named_kwargs),
        (LATTICE_RESULTS_FILENAME, result._result),
        (LATTICE_TRANSPORT_GRAPH_FILENAME, result._lattice.transport_graph),
        (LATTICE_DEPS_FILENAME, result.lattice.metadata["deps"]),
        (LATTICE_CALL_BEFORE_FILENAME, result.lattice.metadata["call_before"]),
        (LATTICE_CALL_AFTER_FILENAME, result.lattice.metadata["call_after"]),
        (LATTICE_COVA_IMPORTS_FILENAME, result.lattice.cova_imports),
        (LATTICE_LATTICE_IMPORTS_FILENAME, result.lattice.lattice_imports),
    ]:
        store_file(data_storage_path, filename, data)

    # Write lattice records to Database
    if not lattice_exists:
        lattice_record_kwarg = {
            "dispatch_id": result.dispatch_id,
            "electron_id": electron_id,
            "status": str(result.status),
            "name": result.lattice.__name__,
            "docstring_filename": LATTICE_DOCSTRING_FILENAME,
            "electron_num": result._num_nodes,
            "completed_electron_num": 0,  # None of the nodes have been executed or completed yet.
            "storage_path": str(data_storage_path),
            "storage_type": LATTICE_STORAGE_TYPE,
            "function_filename": LATTICE_FUNCTION_FILENAME,
            "function_string_filename": LATTICE_FUNCTION_STRING_FILENAME,
            "executor": result.lattice.metadata["executor"],
            "executor_data_filename": LATTICE_EXECUTOR_DATA_FILENAME,
            "workflow_executor": result.lattice.metadata["workflow_executor"],
            "workflow_executor_data_filename": LATTICE_WORKFLOW_EXECUTOR_DATA_FILENAME,
            "error_filename": LATTICE_ERROR_FILENAME,
            "inputs_filename": LATTICE_INPUTS_FILENAME,
            "named_args_filename": LATTICE_NAMED_ARGS_FILENAME,
            "named_kwargs_filename": LATTICE_NAMED_KWARGS_FILENAME,
            "results_filename": LATTICE_RESULTS_FILENAME,
            "transport_graph_filename": LATTICE_TRANSPORT_GRAPH_FILENAME,
            "deps_filename": LATTICE_DEPS_FILENAME,
            "call_before_filename": LATTICE_CALL_BEFORE_FILENAME,
            "call_after_filename": LATTICE_CALL_AFTER_FILENAME,
            "cova_imports_filename": LATTICE_COVA_IMPORTS_FILENAME,
            "lattice_imports_filename": LATTICE_LATTICE_IMPORTS_FILENAME,
            "results_dir": results_dir,
            "root_dispatch_id": result.root_dispatch_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "started_at": result.start_time,
            "completed_at": result.end_time,
        }
        txn_insert_lattices_data(session=session, **lattice_record_kwarg)

    else:
        lattice_record_kwarg = {
            "dispatch_id": result.dispatch_id,
            "status": str(result.status),
            "electron_num": result._num_nodes,
            "updated_at": datetime.now(timezone.utc),
            "started_at": result.start_time,
            "completed_at": result.end_time,
        }
        txn_update_lattices_data(session=session, **lattice_record_kwarg)


def _electron_data(session: Session, result: Result, cancel_requested: bool = False):
    """
    Update electron data
    """
    tg = result.lattice.transport_graph
    dirty_nodes = set(tg.dirty_nodes)
    tg.dirty_nodes.clear()  # Ensure that dirty nodes list is reset once the data is updated
    for node_id in dirty_nodes:
        results_dir = os.environ.get("COVALENT_DATA_DIR") or get_config("dispatcher.results_dir")
        node_path = Path(os.path.join(results_dir, result.dispatch_id, f"node_{node_id}"))

        if not node_path.exists():
            node_path.mkdir()

        node_name = tg.get_node_value(node_id, "name")

        try:
            function_string = tg.get_node_value(node_id, "function_string")
        except KeyError:
            function_string = None

        try:
            node_value = tg.get_node_value(node_id, "value")
        except KeyError:
            node_value = None

        try:
            node_stdout = tg.get_node_value(node_id, "stdout")
        except KeyError:
            node_stdout = None

        try:
            node_stderr = tg.get_node_value(node_id, "stderr")
        except KeyError:
            node_stderr = None

        try:
            node_error = tg.get_node_value(node_id, "error")
        except KeyError:
            node_error = None

        try:
            node_output = tg.get_node_value(node_id, "output")
        except KeyError:
            node_output = None

        executor = tg.get_node_value(node_id, "metadata")["executor"]
        started_at = tg.get_node_value(node_key=node_id, value_key="start_time")
        completed_at = tg.get_node_value(node_key=node_id, value_key="end_time")

        for filename, data in [
            (ELECTRON_FUNCTION_FILENAME, tg.get_node_value(node_id, "function")),
            (ELECTRON_FUNCTION_STRING_FILENAME, function_string),
            (ELECTRON_VALUE_FILENAME, node_value),
            (
                ELECTRON_EXECUTOR_DATA_FILENAME,
                tg.get_node_value(node_id, "metadata")["executor_data"],
            ),
            (ELECTRON_DEPS_FILENAME, tg.get_node_value(node_id, "metadata")["deps"]),
            (
                ELECTRON_CALL_BEFORE_FILENAME,
                tg.get_node_value(node_id, "metadata")["call_before"],
            ),
            (
                ELECTRON_CALL_AFTER_FILENAME,
                tg.get_node_value(node_id, "metadata")["call_after"],
            ),
            (ELECTRON_STDOUT_FILENAME, node_stdout),
            (ELECTRON_STDERR_FILENAME, node_stderr),
            (ELECTRON_ERROR_FILENAME, node_error),
            (ELECTRON_RESULTS_FILENAME, node_output),
        ]:
            store_file(node_path, filename, data)

        electron_exists = (
            session.query(models.Electron, models.Lattice)
            .where(
                models.Electron.parent_lattice_id == models.Lattice.id,
                models.Lattice.dispatch_id == result.dispatch_id,
                models.Electron.transport_graph_node_id == node_id,
            )
            .first()
            is not None
        )

        status = tg.get_node_value(node_key=node_id, value_key="status")
        if not electron_exists:
            electron_record_kwarg = {
                "parent_dispatch_id": result.dispatch_id,
                "transport_graph_node_id": node_id,
                "type": get_electron_type(tg.get_node_value(node_key=node_id, value_key="name")),
                "name": node_name,
                "status": str(status),
                "storage_type": ELECTRON_STORAGE_TYPE,
                "storage_path": str(node_path),
                "function_filename": ELECTRON_FUNCTION_FILENAME,
                "function_string_filename": ELECTRON_FUNCTION_STRING_FILENAME,
                "executor": executor,
                "executor_data_filename": ELECTRON_EXECUTOR_DATA_FILENAME,
                "results_filename": ELECTRON_RESULTS_FILENAME,
                "value_filename": ELECTRON_VALUE_FILENAME,
                "stdout_filename": ELECTRON_STDOUT_FILENAME,
                "stderr_filename": ELECTRON_STDERR_FILENAME,
                "error_filename": ELECTRON_ERROR_FILENAME,
                "deps_filename": ELECTRON_DEPS_FILENAME,
                "call_before_filename": ELECTRON_CALL_BEFORE_FILENAME,
                "call_after_filename": ELECTRON_CALL_AFTER_FILENAME,
                "cancel_requested": cancel_requested,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "started_at": started_at,
                "completed_at": completed_at,
            }
            txn_insert_electrons_data(session=session, **electron_record_kwarg)
        else:
            electron_record_kwarg = {
                "parent_dispatch_id": result.dispatch_id,
                "transport_graph_node_id": node_id,
                "name": node_name,
                "status": str(status),
                "started_at": started_at,
                "updated_at": datetime.now(timezone.utc),
                "completed_at": completed_at,
            }
            update_electrons_data(**electron_record_kwarg)
            if status == Result.COMPLETED:
                update_lattice_completed_electron_num(result.dispatch_id)


def lattice_data(result: Result, electron_id: int = None):
    with workflow_db.session() as session:
        _lattice_data(session, result, electron_id)


def electron_data(result: Result, cancel_requested: bool = False):
    with workflow_db.session() as session:
        _electron_data(session, result, cancel_requested)


def persist_result(result: Result, electron_id: int = None):
    with workflow_db.session() as session:
        _lattice_data(session, result, electron_id)
        if electron_id:
            e_record = (
                session.query(models.Electron).where(models.Electron.id == electron_id).first()
            )
            cancel_requested = txn_get_job_record(session, e_record.job_id)["cancel_requested"]
        else:
            cancel_requested = False
        _electron_data(session, result, cancel_requested)
        txn_upsert_electron_dependency_data(session, result.dispatch_id, result.lattice)
