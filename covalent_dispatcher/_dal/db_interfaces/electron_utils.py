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

"""Mappings between electron attributes and DB records"""

import json

from covalent._shared_files.schemas.electron import ELECTRON_ASSET_KEYS, ELECTRON_METADATA_KEYS
from covalent._shared_files.util_classes import Status

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
    "qelectron_data_exists": "qelectron_data_exists",
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
