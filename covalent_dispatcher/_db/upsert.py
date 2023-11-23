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
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.schemas import electron, lattice, result
from covalent._workflow.transportable_object import TransportableObject

from .._dal.asset import Asset
from .._dal.electron import Electron
from .._dal.job import Job
from .._dal.lattice import Lattice
from .._object_store.local import local_store
from . import models
from .datastore import workflow_db
from .write_result_to_db import get_electron_type, transaction_upsert_electron_dependency_data

app_log = logger.app_log

ELECTRON_FILENAMES = electron.ASSET_FILENAME_MAP
LATTICE_FILENAMES = lattice.ASSET_FILENAME_MAP.copy()
LATTICE_FILENAMES.update(result.ASSET_FILENAME_MAP.copy())

ELECTRON_FUNCTION_FILENAME = ELECTRON_FILENAMES["function"]
ELECTRON_FUNCTION_STRING_FILENAME = ELECTRON_FILENAMES["function_string"]
ELECTRON_VALUE_FILENAME = ELECTRON_FILENAMES["value"]
ELECTRON_STDOUT_FILENAME = ELECTRON_FILENAMES["stdout"]
ELECTRON_STDERR_FILENAME = ELECTRON_FILENAMES["stderr"]
ELECTRON_QELECTRON_DB_FILENAME = ELECTRON_FILENAMES["qelectron_db"]
ELECTRON_ERROR_FILENAME = ELECTRON_FILENAMES["error"]
ELECTRON_RESULTS_FILENAME = ELECTRON_FILENAMES["output"]
ELECTRON_DEPS_FILENAME = ELECTRON_FILENAMES["deps"]
ELECTRON_CALL_BEFORE_FILENAME = ELECTRON_FILENAMES["call_before"]
ELECTRON_CALL_AFTER_FILENAME = ELECTRON_FILENAMES["call_after"]
ELECTRON_STORAGE_TYPE = "file"
LATTICE_FUNCTION_FILENAME = LATTICE_FILENAMES["workflow_function"]
LATTICE_FUNCTION_STRING_FILENAME = LATTICE_FILENAMES["workflow_function_string"]
LATTICE_DOCSTRING_FILENAME = LATTICE_FILENAMES["doc"]
LATTICE_ERROR_FILENAME = LATTICE_FILENAMES["error"]
LATTICE_INPUTS_FILENAME = LATTICE_FILENAMES["inputs"]
LATTICE_NAMED_ARGS_FILENAME = LATTICE_FILENAMES["named_args"]
LATTICE_NAMED_KWARGS_FILENAME = LATTICE_FILENAMES["named_kwargs"]
LATTICE_RESULTS_FILENAME = LATTICE_FILENAMES["result"]
LATTICE_DEPS_FILENAME = LATTICE_FILENAMES["deps"]
LATTICE_CALL_BEFORE_FILENAME = LATTICE_FILENAMES["call_before"]
LATTICE_CALL_AFTER_FILENAME = LATTICE_FILENAMES["call_after"]
LATTICE_COVA_IMPORTS_FILENAME = LATTICE_FILENAMES["cova_imports"]
LATTICE_LATTICE_IMPORTS_FILENAME = LATTICE_FILENAMES["lattice_imports"]
LATTICE_STORAGE_TYPE = "file"

CUSTOM_ASSETS_FIELD = "custom_asset_keys"


def _lattice_data(session: Session, result: Result, electron_id: int = None) -> int:
    """
    Private method to update lattice data in database

    Arg(s)
        session: SQLalchemy session object
        result: Result object associated with the lattice
        electron_id: electron id in the lattice

    Return(s)
        None
    """

    try:
        workflow_func_string = result.lattice.workflow_function_string
    except AttributeError:
        workflow_func_string = None

    # Store all lattice info that belongs in filenames in the results directory
    results_dir = os.environ.get("COVALENT_DATA_DIR") or get_config("dispatcher.results_dir")
    data_storage_path = os.path.join(results_dir, result.dispatch_id)

    assets = {}

    # Ensure that a dispatch is only persisted once
    lattice_recs = Lattice.meta_type.get(
        session,
        fields={"id", "dispatch_id"},
        equality_filters={"dispatch_id": result.dispatch_id},
        membership_filters={},
    )
    if lattice_recs:
        raise RuntimeError("Dispatch already exists in the DB")

    for key, filename, data in [
        ("workflow_function", LATTICE_FUNCTION_FILENAME, result.lattice.workflow_function),
        ("workflow_function_string", LATTICE_FUNCTION_STRING_FILENAME, workflow_func_string),
        ("doc", LATTICE_DOCSTRING_FILENAME, result.lattice.__doc__),
        ("error", LATTICE_ERROR_FILENAME, result.error),
        ("inputs", LATTICE_INPUTS_FILENAME, result.lattice.inputs),
        ("named_args", LATTICE_NAMED_ARGS_FILENAME, result.lattice.named_args),
        ("named_kwargs", LATTICE_NAMED_KWARGS_FILENAME, result.lattice.named_kwargs),
        ("result", LATTICE_RESULTS_FILENAME, result._result),
        ("deps", LATTICE_DEPS_FILENAME, result.lattice.metadata["deps"]),
        ("call_before", LATTICE_CALL_BEFORE_FILENAME, result.lattice.metadata["call_before"]),
        ("call_after", LATTICE_CALL_AFTER_FILENAME, result.lattice.metadata["call_after"]),
        ("cova_imports", LATTICE_COVA_IMPORTS_FILENAME, result.lattice.cova_imports),
        ("lattice_imports", LATTICE_LATTICE_IMPORTS_FILENAME, result.lattice.lattice_imports),
    ]:
        digest = local_store.store_file(data_storage_path, filename, data)
        asset_record_kwargs = {
            "storage_type": LATTICE_STORAGE_TYPE,
            "storage_path": str(data_storage_path),
            "object_key": filename,
            "digest_alg": digest.algorithm,
            "digest": digest.hexdigest,
        }

        assets[key] = Asset.create(session, insert_kwargs=asset_record_kwargs, flush=True)

    # Get custom asset declarations
    lat_metadata = result.lattice.metadata
    if CUSTOM_ASSETS_FIELD in lat_metadata:
        for key in lat_metadata[CUSTOM_ASSETS_FIELD]:
            asset_record_kwargs = {
                "storage_type": LATTICE_STORAGE_TYPE,
                "storage_path": str(data_storage_path),
                "object_key": f"{key}.data",
                "digest_alg": "",
                "digest": "",
            }
            assets[key] = Asset.create(session, insert_kwargs=asset_record_kwargs, flush=True)

    # Write lattice records to Database
    session.flush()

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
        "executor_data": json.dumps(result.lattice.metadata["executor_data"]),
        "workflow_executor": result.lattice.metadata["workflow_executor"],
        "workflow_executor_data": json.dumps(result.lattice.metadata["workflow_executor_data"]),
        "error_filename": LATTICE_ERROR_FILENAME,
        "inputs_filename": LATTICE_INPUTS_FILENAME,
        "named_args_filename": LATTICE_NAMED_ARGS_FILENAME,
        "named_kwargs_filename": LATTICE_NAMED_KWARGS_FILENAME,
        "results_filename": LATTICE_RESULTS_FILENAME,
        "deps_filename": LATTICE_DEPS_FILENAME,
        "call_before_filename": LATTICE_CALL_BEFORE_FILENAME,
        "call_after_filename": LATTICE_CALL_AFTER_FILENAME,
        "cova_imports_filename": LATTICE_COVA_IMPORTS_FILENAME,
        "lattice_imports_filename": LATTICE_LATTICE_IMPORTS_FILENAME,
        "results_dir": results_dir,
        "root_dispatch_id": result.root_dispatch_id,
        "python_version": result.lattice.python_version,
        "covalent_version": result.lattice.covalent_version,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "started_at": result.start_time,
        "completed_at": result.end_time,
    }
    lattice_row = Lattice.meta_type.create(session, insert_kwargs=lattice_record_kwarg, flush=True)
    lattice_record = Lattice(session, lattice_row, bare=True, keys={"id"}, electron_keys={"id"})

    lattice_asset_links = [
        lattice_record.associate_asset(session, key, asset.id) for key, asset in assets.items()
    ]
    session.flush()

    return lattice_row.id


def _electron_data(
    session: Session, lattice_id: int, result: Result, cancel_requested: bool = False
) -> dict:
    """
    Update electron data in database

    Arg(s)
        session: SQLalchemy session object
        result: Result object associated with the lattice
        cancel_requested: Boolean indicating whether electron was requested to be cancelled

    Return(s)
        None
    """

    node_id_eid_map = {}
    tg = result.lattice.transport_graph
    dirty_nodes = set(tg.dirty_nodes)
    tg.dirty_nodes.clear()  # Ensure that dirty nodes list is reset once the data is updated

    # Collect task groups and create a job record for each group
    task_groups = {}
    for node_id in dirty_nodes:
        gid = tg.get_node_value(node_id, "task_group_id")
        if gid not in task_groups:
            task_groups[gid] = [node_id]
        else:
            task_groups[gid].append(node_id)

    timestamp = datetime.now(timezone.utc)

    for gid, nodes in task_groups.items():
        job_row = Job.create(
            session, insert_kwargs={"cancel_requested": cancel_requested}, flush=True
        )

        app_log.debug(f"Created job record for task group {result.dispatch_id}:{gid}")

        for node_id in nodes:
            results_dir = os.environ.get("COVALENT_DATA_DIR") or get_config(
                "dispatcher.results_dir"
            )
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
                node_value = TransportableObject(None)

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
                node_output = TransportableObject(None)

            try:
                node_qelectron_data_exists = tg.get_node_value(node_id, "qelectron_data_exists")
            except KeyError:
                node_qelectron_data_exists = False

            try:
                node_qelectron_data = tg.get_node_value(node_id, "qelectron_db")
            except KeyError:
                node_qelectron_data = bytes()

            executor = tg.get_node_value(node_id, "metadata")["executor"]
            started_at = tg.get_node_value(node_key=node_id, value_key="start_time")
            completed_at = tg.get_node_value(node_key=node_id, value_key="end_time")

            assets = {}

            for key, filename, data in [
                ("function", ELECTRON_FUNCTION_FILENAME, tg.get_node_value(node_id, "function")),
                ("function_string", ELECTRON_FUNCTION_STRING_FILENAME, function_string),
                ("value", ELECTRON_VALUE_FILENAME, node_value),
                ("deps", ELECTRON_DEPS_FILENAME, tg.get_node_value(node_id, "metadata")["deps"]),
                (
                    "call_before",
                    ELECTRON_CALL_BEFORE_FILENAME,
                    tg.get_node_value(node_id, "metadata")["call_before"],
                ),
                (
                    "call_after",
                    ELECTRON_CALL_AFTER_FILENAME,
                    tg.get_node_value(node_id, "metadata")["call_after"],
                ),
                ("stdout", ELECTRON_STDOUT_FILENAME, node_stdout),
                ("stderr", ELECTRON_STDERR_FILENAME, node_stderr),
                ("qelectron_db", ELECTRON_QELECTRON_DB_FILENAME, node_qelectron_data),
                ("error", ELECTRON_ERROR_FILENAME, node_error),
                ("output", ELECTRON_RESULTS_FILENAME, node_output),
            ]:
                digest = local_store.store_file(node_path, filename, data)
                asset_record_kwargs = {
                    "storage_type": ELECTRON_STORAGE_TYPE,
                    "storage_path": str(node_path),
                    "object_key": filename,
                    "digest_alg": digest.algorithm,
                    "digest": digest.hexdigest,
                }

                assets[key] = Asset.create(session, insert_kwargs=asset_record_kwargs, flush=True)

            # Register custom assets
            node_metadata = tg.get_node_value(node_id, "metadata")
            if CUSTOM_ASSETS_FIELD in node_metadata:
                for key in node_metadata[CUSTOM_ASSETS_FIELD]:
                    asset_record_kwargs = {
                        "storage_type": LATTICE_STORAGE_TYPE,
                        "storage_path": str(node_path),
                        "object_key": f"{key}.data",
                        "digest_alg": "",
                        "digest": "",
                    }
                    assets[key] = Asset.create(
                        session, insert_kwargs=asset_record_kwargs, flush=True
                    )

            status = tg.get_node_value(node_key=node_id, value_key="status")
            executor_data = tg.get_node_value(node_id, "metadata")["executor_data"]

            electron_record_kwarg = {
                "parent_lattice_id": lattice_id,
                "transport_graph_node_id": node_id,
                "task_group_id": gid,
                "type": get_electron_type(tg.get_node_value(node_key=node_id, value_key="name")),
                "name": node_name,
                "status": str(status),
                "storage_type": ELECTRON_STORAGE_TYPE,
                "storage_path": str(node_path),
                "function_filename": ELECTRON_FUNCTION_FILENAME,
                "function_string_filename": ELECTRON_FUNCTION_STRING_FILENAME,
                "executor": executor,
                "executor_data": json.dumps(executor_data),
                "results_filename": ELECTRON_RESULTS_FILENAME,
                "value_filename": ELECTRON_VALUE_FILENAME,
                "stdout_filename": ELECTRON_STDOUT_FILENAME,
                "stderr_filename": ELECTRON_STDERR_FILENAME,
                "error_filename": ELECTRON_ERROR_FILENAME,
                "deps_filename": ELECTRON_DEPS_FILENAME,
                "call_before_filename": ELECTRON_CALL_BEFORE_FILENAME,
                "call_after_filename": ELECTRON_CALL_AFTER_FILENAME,
                "qelectron_data_exists": node_qelectron_data_exists,
                "job_id": job_row.id,
                "created_at": timestamp,
                "updated_at": timestamp,
                "started_at": started_at,
                "completed_at": completed_at,
            }
            electron_row = Electron.meta_type.create(
                session,
                insert_kwargs=electron_record_kwarg,
                flush=True,
            )
            electron_record = Electron(session, electron_row, keys={"id"})

            node_id_eid_map[node_id] = electron_row.id

            electron_asset_links = [
                electron_record.associate_asset(session, key, asset.id)
                for key, asset in assets.items()
            ]
            session.flush()

    return node_id_eid_map


def persist_result(result: Result, electron_id: int = None) -> None:
    """
    Persist the result object of the lattice recursively into the database

    Arg(s)
        result: Result object associated with the lattice
        electron_id: ID of the electron within the lattice

    Return(s)
        None
    """
    with workflow_db.session() as session:
        parent_lattice_id = _lattice_data(session, result, electron_id)
        if electron_id:
            e_record = (
                session.query(models.Electron).where(models.Electron.id == electron_id).first()
            )
            job_record = Job.get_by_primary_key(session, e_record.job_id)
            cancel_requested = job_record.cancel_requested
        else:
            cancel_requested = False
        node_id_eid_map = _electron_data(session, parent_lattice_id, result, cancel_requested)
        transaction_upsert_electron_dependency_data(session, result.dispatch_id, result.lattice)
