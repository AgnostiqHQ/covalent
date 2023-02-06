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

"""DB-backed electron"""

from typing import Any, Dict

from sqlalchemy.orm import Session

from covalent._shared_files.util_classes import Status

from .._db import models
from .._db.utils import resolve_sub_dispatch_id
from .asset import Asset
from .base import DispatchedObject
from .db_interfaces.electron_utils import (
    ASSET_KEYS,
    METADATA_KEYS,
    _meta_record_map,
    _to_asset_meta,
    _to_db_meta,
    _to_pure_meta,
)


def get_status_filter(raw: str):
    return Status(raw)


def set_status_filter(stat: Status):
    return str(stat)


get_filters = {key: lambda x: x for key in METADATA_KEYS.union(ASSET_KEYS)}

set_filters = {key: lambda x: x for key in METADATA_KEYS.union(ASSET_KEYS)}

custom_get_filters = {"status": get_status_filter, "type": lambda x: x}

custom_set_filters = {"status": set_status_filter}

get_filters.update(custom_get_filters)
set_filters.update(custom_set_filters)


class Electron(DispatchedObject):
    def __init__(self, record: models.Electron):

        pure_metadata = _to_pure_meta(record)
        asset_metadata = _to_asset_meta(record)
        db_metadata = _to_db_meta(record)

        self._pure_metadata = pure_metadata
        self._db_metadata = db_metadata
        self._assets = {}

        self.node_id = record.transport_graph_node_id
        self._electron_id = db_metadata["electron_id"]
        self._lattice_id = db_metadata["lattice_id"]
        self._storage_path = db_metadata["storage_path"]
        self._storage_type = db_metadata["storage_type"]

        for name in asset_metadata:
            self._assets[name] = Asset(self._storage_path, asset_metadata[name])

    @property
    def pure_metadata(self) -> Dict:
        return self._pure_metadata

    @pure_metadata.setter
    def pure_metadata(self, meta: Dict):
        self._pure_metadata = meta

    @property
    def db_metadata(self):
        return self._db_metadata

    @db_metadata.setter
    def db_metadata(self, meta: Dict):
        self._db_metadata = meta

    @property
    def assets(self):
        return self._assets

    def _get_db_record(self, session) -> models.Electron:
        record = (
            session.query(models.Electron).where(models.Electron.id == self._electron_id).first()
        )
        return record

    def _to_pure_meta(self, record):
        return _to_pure_meta(record)

    def _to_db_meta(self, record):
        return _to_db_meta(record)

    def meta_record_map(self, key: str) -> str:
        return _meta_record_map[key]

    def get_value(self, key: str, session: Session = None, refresh: bool = True):
        if key == "sub_dispatch_id":
            return resolve_sub_dispatch_id(self._electron_id)
        else:
            return get_filters[key](super().get_value(key, session, refresh))

    def set_value(self, key: str, val: Any, session: Session = None) -> None:
        super().set_value(key, set_filters[key](val), session)
