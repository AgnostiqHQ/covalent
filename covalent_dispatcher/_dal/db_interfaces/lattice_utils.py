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

from typing import Dict

from sqlalchemy.orm import Session

from ..._db import models

ATTRIBUTES = {
    "workflow_function",
    "workflow_function_string",
    "transport_graph",
    "metadata",
    "__name__",
    "__doc__",
    "named_args",
    "named_kwargs",
    "cova_imports",
    "lattice_imports",
}


METADATA_KEYS = {
    "__name__",
    # metadata
    "executor",
    "workflow_executor",
}

ASSET_KEYS = {
    "workflow_function",
    "workflow_function_string",
    "__doc__",
    "named_args",
    "named_kwargs",
    "cova_imports",
    "lattice_imports",
    # metadata
    "executor_data",
    "workflow_executor_data",
    "deps",
    "call_before",
    "call_after",
}

_meta_record_map = {
    "__name__": "name",
    "executor": "executor",
    "workflow_executor": "workflow_executor",
}

_asset_record_map = {
    "workflow_function": "function_filename",
    "workflow_function_string": "function_string_filename",
    "__doc__": "docstring_filename",
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


def _to_pure_meta(session: Session, record: models.Lattice) -> Dict:
    pure_metadata = {k: getattr(record, v) for k, v in _meta_record_map.items()}

    return pure_metadata


def _to_asset_meta(session: Session, record: models.Lattice) -> Dict:
    asset_metadata = {k: getattr(record, v) for k, v in _asset_record_map.items()}
    return asset_metadata


def _to_db_meta(session: Session, record: models.Lattice) -> Dict:
    db_metadata = {
        "electron_id": record.electron_id,
        "lattice_id": record.id,
        "storage_path": record.storage_path,
        "storage_type": record.storage_type,
    }
    return db_metadata
