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

from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..._db import models

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


METADATA_KEYS = {
    "task_group_id",
    "name",
    "start_time",
    "end_time",
    "status",
    # electron metadata
    "executor",
}

ASSET_KEYS = {
    "function",
    "function_string",
    "output",
    "value",
    "error",
    "stdout",
    "stderr",
    # electron metadata
    "executor_data",
    "deps",
    "call_before",
    "call_after",
}

_meta_record_map = {
    "task_group_id": "task_group_id",
    "name": "name",
    "start_time": "started_at",
    "end_time": "completed_at",
    "status": "status",
    "executor": "executor",
}

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


def _to_pure_meta(session: Session, record: models.Electron):
    pure_metadata = {k: getattr(record, v) for k, v in _meta_record_map.items()}

    return pure_metadata


def _to_asset_meta(session: Session, record: models.Electron):
    # get asset ids
    stmt = select(models.ElectronAsset).where(models.ElectronAsset.electron_id == record.id)
    electron_asset_links = session.scalars(stmt).all()
    return {x.key: x.asset_id for x in electron_asset_links}


def _get_asset_ids(session: Session, electron_id: int, keys: List[str]) -> Dict[str, int]:
    stmt = select(models.ElectronAsset).where(models.ElectronAsset.electron_id == electron_id)

    if len(keys) > 0:
        stmt = stmt.where(models.ElectronAsset.key.in_(keys))

    records = session.scalars(stmt).all()
    return {x.key: x.asset_id for x in records}


def _to_db_meta(session: Session, record: models.Electron):
    db_metadata = {
        "electron_id": record.id,
        "lattice_id": record.parent_lattice_id,
        "type": record.type,
        "storage_path": record.storage_path,
        "storage_type": record.storage_type,
    }
    return db_metadata
