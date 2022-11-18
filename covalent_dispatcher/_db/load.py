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


from covalent._shared_files import logger

from . import models
from .datastore import workflow_db
from .write_result_to_db import load_file

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


meta_loader_map = {
    "executor": None,
    "executor_data": None,
    "deps": None,
    "call_before": None,
    "call_after": None,
}

# Metadata only
node_meta_keys = {
    "node_name",
    "start_time",
    "end_time",
    "status",
}


def _record_to_node_dict(record: models.Electron):
    """Format an Electron record according to tg node attributes"""

    meta = {
        "executor": record.executor,
        "executor_data": record.executor_data_filename,
        "deps": record.deps_filename,
        "call_before": record.call_before_filename,
        "call_after": record.call_after_filename,
    }

    node_meta = {
        "metadata": meta,
        "node_name": record.name,
        "start_time": str(record.started_at),
        "end_time": str(record.completed_at),
        "status": record.status,
        "callable": record.function_filename,
        "output": record.results_filename,
        "error": record.error_filename,
        "sublattice_result": None,
        "stdout": record.stdout_filename,
        "stderr": record.stderr_filename,
    }

    return node_meta


def _record_to_metadata(record: models.Electron, key: str):
    node_meta = _record_to_node_dict(record)
    return node_meta[key]


def _record_to_value(record: models.Electron, key: str):
    storage_path = record.storage_path
    node_meta = _record_to_node_dict(record)
    return load_file(storage_path, node_meta[key])


def _electron_record(dispatch_id: str, node_id: int) -> models.Electron:
    with workflow_db.session() as session:
        record = (
            session.query(models.Lattice, models.Electron)
            .where(
                models.Lattice.dispatch_id == dispatch_id,
                models.Electron.parent_lattice_id == models.Lattice.id,
                models.Electron.transport_graph_node_id == node_id,
            )
            .first()
        )
        app_log.debug(f"{record}")
        session.expunge(record.Electron)
        return record.Electron


node_loader_map = {
    "metadata": None,
    "node_name": _record_to_metadata,
    "start_time": _record_to_metadata,
    "end_time": _record_to_metadata,
    "status": _record_to_metadata,
    "callable": _record_to_value,
    "output": _record_to_value,
    "error": _record_to_value,
    "sublattice_result": None,
    "stdout": _record_to_value,
    "stderr": _record_to_value,
}


def load_node_attribute(dispatch_id: str, node_id: int, key: str):
    record = _electron_record(dispatch_id, node_id)
    loader = node_loader_map[key]
    return loader(record, key)
