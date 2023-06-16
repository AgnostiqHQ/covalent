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

"""Mappings between electron attributes and DB records"""

import json

from covalent._shared_files.schemas.electron import ELECTRON_ASSET_KEYS, ELECTRON_METADATA_KEYS
from covalent._shared_files.util_classes import Status

ATTRIBUTES = {
    "name",
    "start_time",
    "end_time",
    "status",
    "sub_dispatch_id",
    "function",
    "function_string",
    "output",
    "value",
    "error",
    "stdout",
    "stderr",
    "metadata",
}

METADATA_KEYS = ELECTRON_METADATA_KEYS
ASSET_KEYS = ELECTRON_ASSET_KEYS

COMPUTED_FIELDS = {"sub_dispatch_id"}

_meta_record_map = {
    "node_id": "transport_graph_node_id",
    "task_group_id": "task_group_id",
    "name": "name",
    "start_time": "started_at",
    "end_time": "completed_at",
    "status": "status",
    "executor": "executor",
    "executor_data": "executor_data",
}

_db_meta_record_map = {
    "id": "id",
    "parent_lattice_id": "parent_lattice_id",
    "type": "type",
    "storage_path": "storage_path",
    "storage_type": "storage_type",
    "job_id": "job_id",
}

_meta_record_map.update(_db_meta_record_map)

# Obsoleted by ElectronAsset table
_asset_record_map = {
    "function": "function_filename",
    "function_string": "function_string_filename",
    "output": "results_filename",
    "value": "value_filename",
    "error": "error_filename",
    "stdout": "stdout_filename",
    "stderr": "stderr_filename",
    "executor_data": "executor_data_filename",
    "deps": "deps_filename",
    "call_before": "call_before_filename",
    "call_after": "call_after_filename",
}


def identity(x):
    return x


def get_status_filter(raw: str):
    return Status(raw)


def set_status_filter(stat: Status):
    return str(stat)


def get_executor_data_filter(raw: str):
    return json.loads(raw)


def set_executor_data_filter(object_dict: dict):
    return json.dumps(object_dict)


custom_get_filters = {
    "status": get_status_filter,
    "executor_data": get_executor_data_filter,
    "type": identity,
    "sub_dispatch_id": identity,
}

custom_set_filters = {"status": set_status_filter, "executor_data": set_executor_data_filter}


get_filters = {key: identity for key in METADATA_KEYS.union(ASSET_KEYS)}

set_filters = {key: identity for key in METADATA_KEYS.union(ASSET_KEYS)}

get_filters.update(custom_get_filters)
set_filters.update(custom_set_filters)
