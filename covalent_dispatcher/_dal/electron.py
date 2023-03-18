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
from .db_interfaces.electron_utils import _meta_record_map, _to_meta, get_filters, set_filters

ELECTRON_KEYS = list(_meta_record_map.keys())


class Electron(DispatchedObject):
    model = models.Electron
    asset_link_model = models.ElectronAsset

    def __init__(self, session: Session, record: models.Electron, *, keys: List = ELECTRON_KEYS):
        self._id = record.id
        self._keys = keys
        self._metadata = _to_meta(session, record, self._keys)
        self._assets = {}

        self._record = record

        self.node_id = record.transport_graph_node_id
        self._electron_id = record.id

    @property
    def keys(self) -> list:
        return self._keys

    @property
    def metadata(self) -> Dict:
        return self._metadata

    @metadata.setter
    def metadata(self, meta: Dict):
        self._metadata = meta

    @property
    def computed_fields(self) -> Dict:
        return {"sub_dispatch_id": resolve_sub_dispatch_id}

    @property
    def assets(self):
        return self._assets

    def _to_meta(self, session: Session, record: models.Electron, keys: List):
        return _to_meta(session, record, self.keys)

    @property
    def meta_record_map(self) -> Dict:
        return _meta_record_map

    def get_value(self, key: str, session: Session = None, refresh: bool = True):
        return get_filters[key](super().get_value(key, session, refresh))

    def set_value(self, key: str, val: Any, session: Session = None) -> None:
        super().set_value(key, set_filters[key](val), session)


def resolve_sub_dispatch_id(obj: Electron, session: Session) -> str:
    stmt = select(models.Lattice.dispatch_id).where(models.Lattice.electron_id == obj._electron_id)
    record = session.scalars(stmt).first()
    return record
