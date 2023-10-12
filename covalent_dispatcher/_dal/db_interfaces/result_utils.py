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

"""Mappings between result attributes and DB records"""


from covalent._shared_files.schemas import result
from covalent._shared_files.util_classes import Status

from . import lattice_utils

ATTRIBUTES = {
    "start_time",
    "end_time",
    "results_dir",
    "lattice",
    "dispatch_id",
    "root_dispatch_id",
    "electron_id",
    "status",
    "task_failed",
    "task_cancelled",
    "result",
    "num_nodes",
    "error",
}

METADATA_KEYS = result.METADATA_KEYS.copy()
METADATA_KEYS.update({"results_dir", "electron_id"})
ASSET_KEYS = result.ASSET_KEYS


_meta_record_map = {
    "start_time": "started_at",
    "end_time": "completed_at",
    "results_dir": "results_dir",
    "dispatch_id": "dispatch_id",
    "root_dispatch_id": "root_dispatch_id",
    "electron_id": "electron_id",
    "status": "status",
    "num_nodes": "electron_num",
    "completed_electron_num": "completed_electron_num",
}

_db_meta_record_map = {
    "id": "id",
    "electron_id": "electron_id",
    "storage_path": "storage_path",
    "storage_type": "storage_type",
    "completed_electron_num": "completed_electron_num",
}

_meta_record_map.update(_db_meta_record_map)
_meta_record_map.update(lattice_utils._meta_record_map)


# Obsoleted by LatticeAsset table
_asset_record_map = {
    "result": "results_filename",
    "error": "error_filename",
}


def get_status_filter(raw: str):
    return Status(raw)


def set_status_filter(stat: Status):
    return str(stat)


get_filters = {key: lambda x: x for key in METADATA_KEYS.union(ASSET_KEYS)}

set_filters = {key: lambda x: x for key in METADATA_KEYS.union(ASSET_KEYS)}

custom_get_filters = {"status": get_status_filter, "completed_electron_num": lambda x: x}

custom_set_filters = {"status": set_status_filter, "completed_electron_num": lambda x: x}

get_filters.update(custom_get_filters)
set_filters.update(custom_set_filters)
