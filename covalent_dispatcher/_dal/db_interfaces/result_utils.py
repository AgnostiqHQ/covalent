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

from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from covalent._shared_files.util_classes import Status

from ..._db import models

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
    "inputs",
    "error",
}

METADATA_KEYS = {
    "start_time",
    "end_time",
    "results_dir",
    "dispatch_id",
    "root_dispatch_id",
    "electron_id",
    "status",
    "num_nodes",
}


ASSET_KEYS = {
    "inputs",
    "result",
    "error",
}

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

# Obsoleted by LatticeAsset table
_asset_record_map = {
    "inputs": "inputs_filename",
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


def _to_meta(session: Session, record: models.Lattice, keys: List):
    metadata = {k: getattr(record, _meta_record_map[k]) for k in keys}

    return metadata


def _to_asset_meta(session: Session, record: models.Lattice):
    # get asset ids
    stmt = select(models.LatticeAsset).where(models.LatticeAsset.lattice_id == record.id)
    lattice_asset_links = session.scalars(stmt).all()
    return {x.key: x.asset_id for x in lattice_asset_links}


def _get_asset_ids(session: Session, lattice_id: int, keys: List[str]) -> Dict[str, int]:
    stmt = select(models.LatticeAsset).where(models.LatticeAsset.lattice_id == lattice_id)

    if len(keys) > 0:
        stmt = stmt.where(models.LatticeAsset.key.in_(keys))

    records = session.scalars(stmt).all()
    return {x.key: x.asset_id for x in records}
