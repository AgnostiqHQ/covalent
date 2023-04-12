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

"""Mappings between lattice attributes and DB records"""

import json
from typing import Dict, List

from sqlalchemy.orm import Session

from ..._db import models

ATTRIBUTES = {
    "workflow_function",
    "workflow_function_string",
    "transport_graph",
    "metadata",
    "name",
    "doc",
    "named_args",
    "named_kwargs",
    "cova_imports",
    "lattice_imports",
}


METADATA_KEYS = {
    "name",
    # metadata
    "executor",
    "workflow_executor",
    "executor_data",
    "workflow_executor_data",
}

ASSET_KEYS = {
    "workflow_function",
    "workflow_function_string",
    "doc",
    "named_args",
    "named_kwargs",
    "cova_imports",
    "lattice_imports",
    # metadata
    "deps",
    "call_before",
    "call_after",
}

_meta_record_map = {
    "name": "name",
    "executor": "executor",
    "executor_data": "executor_data",
    "workflow_executor": "workflow_executor",
    "workflow_executor_data": "workflow_executor_data",
}

_db_meta_record_map = {
    "electron_id": "electron_id",
    "id": "id",
    "storage_path": "storage_path",
    "storage_type": "storage_type",
}

_meta_record_map.update(_db_meta_record_map)

# Obsoleted by LatticeAsset table
_asset_record_map = {
    "workflow_function": "function_filename",
    "workflow_function_string": "function_string_filename",
    "doc": "docstring_filename",
    "named_args": "named_args_filename",
    "named_kwargs": "named_kwargs_filename",
    "cova_imports": "cova_imports_filename",
    "lattice_imports": "lattice_imports_filename",
    "executor_data": "executor_data_filename",
    "workflow_executor_data": "workflow_executor_data_filename",
    "deps": "deps_filename",
    "call_before": "call_before_filename",
    "call_after": "call_after_filename",
}


def get_executor_data_filter(raw: str):
    return json.loads(raw)


def set_executor_data_filter(object_dict: dict):
    return json.dumps(object_dict)


def identity(x):
    return x


custom_get_filters = {
    "executor_data": get_executor_data_filter,
    "workflow_executor_data": get_executor_data_filter,
}
custom_set_filters = {
    "executor_data": set_executor_data_filter,
    "workflow_executor_data": set_executor_data_filter,
}


get_filters = {key: identity for key in METADATA_KEYS.union(ASSET_KEYS)}

set_filters = {key: identity for key in METADATA_KEYS.union(ASSET_KEYS)}

get_filters.update(custom_get_filters)
set_filters.update(custom_set_filters)


def _to_meta(session: Session, record: models.Lattice, keys: List) -> Dict:
    metadata = {k: getattr(record, _meta_record_map[k]) for k in keys}
    return metadata
