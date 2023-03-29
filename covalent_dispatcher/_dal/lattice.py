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

from typing import Any, List

from sqlalchemy.orm import Session

from .._db import models
from .base import DispatchedObject
from .controller import Record
from .db_interfaces.lattice_utils import ASSET_KEYS  # nopycln: import
from .db_interfaces.lattice_utils import METADATA_KEYS  # nopycln: import
from .db_interfaces.lattice_utils import _meta_record_map, get_filters, set_filters
from .tg import ELECTRON_KEYS, get_compute_graph

LATTICE_KEYS = list(_meta_record_map.keys())


class LatticeMeta(Record[models.Lattice]):
    model = models.Lattice


class LatticeAsset(Record[models.LatticeAsset]):
    model = models.LatticeAsset


class Lattice(DispatchedObject):
    meta_type = LatticeMeta
    asset_link_type = LatticeAsset

    metadata_keys = LATTICE_KEYS

    def __init__(
        self,
        session: Session,
        record: models.Lattice,
        bare: bool = False,
        *,
        keys: List = LATTICE_KEYS,
        electron_keys: List = ELECTRON_KEYS,
    ):
        self._id = record.id
        self._keys = keys
        fields = set(map(Lattice.meta_record_map, keys))

        self._metadata = LatticeMeta(session, record, fields=fields)
        self._assets = {}
        self._lattice_id = record.id

        self.transport_graph = get_compute_graph(self._lattice_id, bare, keys=electron_keys)

    @property
    def query_keys(self) -> List:
        return self._keys

    @property
    def metadata(self) -> LatticeMeta:
        return self._metadata

    @property
    def assets(self):
        return self._assets

    @classmethod
    def meta_record_map(cls: DispatchedObject, key: str) -> str:
        return _meta_record_map[key]

    @property
    def __name__(self):
        return self.get_value("__name__")

    @property
    def workflow_function(self):
        return self.get_value("workflow_function")

    def get_value(self, key: str, session: Session = None, refresh: bool = True):
        return get_filters[key](super().get_value(key, session, refresh))

    def set_value(self, key: str, val: Any, session: Session = None) -> None:
        super().set_value(key, set_filters[key](val), session)
