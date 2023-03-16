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

from typing import Dict, List

from sqlalchemy import select
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


def _to_meta(session: Session, record: models.Lattice) -> Dict:
    metadata = {k: getattr(record, v) for k, v in _meta_record_map.items()}
    return metadata


def _get_asset_ids(session: Session, lattice_id: int, keys: List[str]) -> Dict[str, int]:
    stmt = select(models.LatticeAsset).where(models.LatticeAsset.lattice_id == lattice_id)

    if len(keys) > 0:
        stmt = stmt.where(models.LatticeAsset.key.in_(keys))

    records = session.scalars(stmt).all()
    return {x.key: x.asset_id for x in records}
