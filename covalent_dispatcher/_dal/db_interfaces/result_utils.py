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
