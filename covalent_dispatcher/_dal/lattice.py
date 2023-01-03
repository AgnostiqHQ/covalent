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

"""DB-backed lattice"""

from typing import Dict

from sqlalchemy.orm import Session

from .._db import models
from .asset import Asset
from .base import DispatchedObject
from .db_interfaces.lattice_utils import (
    ASSET_KEYS,
    METADATA_KEYS,
    _asset_record_map,
    _meta_record_map,
    _to_asset_meta,
    _to_db_meta,
    _to_pure_meta,
)
from .tg import get_compute_graph


class Lattice(DispatchedObject):
    def __init__(self, record: models.Lattice, bare: bool = False):
        pure_metadata = _to_pure_meta(record)
        asset_metadata = _to_asset_meta(record)
        db_metadata = _to_db_meta(record)

        self._pure_metadata = pure_metadata
        self._db_metadata = db_metadata
        self._assets = {}

        self._lattice_id = db_metadata["lattice_id"]
        self._storage_path = db_metadata["storage_path"]
        self._storage_type = db_metadata["storage_type"]

        for name in asset_metadata:
            self._assets[name] = Asset(self._storage_path, asset_metadata[name])

        self.transport_graph = get_compute_graph(self._lattice_id, bare)

    @property
    def pure_metadata(self):
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

    def _get_db_record(self, session: Session) -> models.Lattice:
        record = session.query(models.Lattice).where(models.Lattice.id == self._lattice_id).first()
        return record

    def meta_record_map(self, key: str) -> str:
        return _meta_record_map[key]

    def _to_pure_meta(self, record):
        return _to_pure_meta(record)

    def _to_db_meta(self, record):
        return _to_db_meta(record)

    @property
    def __name__(self):
        return self.get_value("__name__")

    def get_metadata(self, key: str):
        if key in METADATA_KEYS or key in ASSET_KEYS:
            return self.get_value(key)
        else:
            return None

    @property
    def workflow_function(self):
        return self.get_value("workflow_function")
