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

"""DB-backed electron"""

from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from .._db import models
from .base import DispatchedObject
from .controller import Record
from .db_interfaces.electron_utils import ASSET_KEYS  # nopycln: import
from .db_interfaces.electron_utils import METADATA_KEYS  # nopycln: import
from .db_interfaces.electron_utils import _meta_record_map, get_filters, set_filters

ELECTRON_KEYS = list(_meta_record_map.keys())


class ElectronMeta(Record[models.Electron]):
    model = models.Electron


class ElectronAsset(Record[models.ElectronAsset]):
    model = models.ElectronAsset


class Electron(DispatchedObject[ElectronMeta, ElectronAsset]):
    meta_type = ElectronMeta
    asset_link_type = ElectronAsset

    metadata_keys = ELECTRON_KEYS

    def __init__(self, session: Session, record: models.Electron, *, keys: List = ELECTRON_KEYS):
        self._id = record.id
        self._keys = keys

        fields = set(map(Electron.meta_record_map, keys))

        self._metadata = ElectronMeta(session, record, fields=fields)
        self._assets = {}
        self._electron_id = record.id

        self.node_id = record.transport_graph_node_id

    @property
    def query_keys(self) -> list:
        return self._keys

    @property
    def metadata(self) -> ElectronMeta:
        return self._metadata

    @property
    def computed_fields(self) -> Dict:
        return {"sub_dispatch_id": resolve_sub_dispatch_id}

    @property
    def assets(self):
        return self._assets

    @classmethod
    def meta_record_map(cls: DispatchedObject, key: str) -> str:
        return _meta_record_map[key]

    def get_value(self, key: str, session: Session = None, refresh: bool = True):
        return get_filters[key](super().get_value(key, session, refresh))

    def set_value(self, key: str, val: Any, session: Session = None) -> None:
        super().set_value(key, set_filters[key](val), session)


def resolve_sub_dispatch_id(obj: Electron, session: Session) -> str:
    stmt = select(models.Lattice.dispatch_id).where(models.Lattice.electron_id == obj._electron_id)
    record = session.scalars(stmt).first()
    return record
