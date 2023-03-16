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

from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from .._db import models
from .base import DispatchedObject
from .db_interfaces.electron_utils import ASSET_KEYS  # nopycln: import
from .db_interfaces.electron_utils import METADATA_KEYS  # nopycln: import
from .db_interfaces.electron_utils import (
    _get_asset_ids,
    _meta_record_map,
    _to_meta,
    get_filters,
    set_filters,
)


class Electron(DispatchedObject):
    def __init__(self, session: Session, record: models.Electron):
        metadata = _to_meta(session, record)

        self._metadata = metadata
        self._assets = {}

        self._record = record

        self.node_id = record.transport_graph_node_id
        self._electron_id = metadata["id"]

    @property
    def metadata(self) -> Dict:
        return self._metadata

    @metadata.setter
    def metadata(self, meta: Dict):
        self._metadata = meta

    def get_asset_ids(self, session: Session, keys: List[str]) -> Dict[str, int]:
        return _get_asset_ids(session, self._electron_id, keys)

    @property
    def computed_fields(self) -> Dict:
        return {"sub_dispatch_id": resolve_sub_dispatch_id}

    @property
    def assets(self):
        return self._assets

    def _get_db_record(self, session) -> models.Electron:
        record = (
            session.query(models.Electron).where(models.Electron.id == self._electron_id).first()
        )
        return record

    def _to_meta(self, session: Session, record):
        return _to_meta(session, record)

    def meta_record_map(self, key: str) -> str:
        return _meta_record_map[key]

    def get_value(self, key: str, session: Session = None, refresh: bool = True):
        return get_filters[key](super().get_value(key, session, refresh))

    def set_value(self, key: str, val: Any, session: Session = None) -> None:
        super().set_value(key, set_filters[key](val), session)


def resolve_sub_dispatch_id(obj: Electron, session: Session) -> str:
    stmt = select(models.Lattice.dispatch_id).where(models.Lattice.electron_id == obj._electron_id)
    record = session.scalars(stmt).first()
    return record
