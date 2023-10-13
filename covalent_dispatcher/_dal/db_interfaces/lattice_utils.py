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

"""Mappings between lattice attributes and DB records"""

import json

from covalent._shared_files.schemas import lattice

ATTRIBUTES = {
    "workflow_function",
    "workflow_function_string",
    "transport_graph",
    "metadata",
    "name",
    "doc",
    "inputs",
    "named_args",
    "named_kwargs",
    "cova_imports",
    "lattice_imports",
}

METADATA_KEYS = lattice.LATTICE_METADATA_KEYS.copy()
METADATA_KEYS.remove("__name__")
METADATA_KEYS.add("name")

ASSET_KEYS = lattice.LATTICE_ASSET_KEYS.copy()
ASSET_KEYS.remove("__doc__")
ASSET_KEYS.add("doc")


_meta_record_map = {
    "name": "name",
    "python_version": "python_version",
    "covalent_version": "covalent_version",
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
    "inputs": "inputs_filename",
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
