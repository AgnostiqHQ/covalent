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

from typing import Dict, List

from sqlalchemy.orm import Session

from .._db import models
from .base import DispatchedObject
from .db_interfaces.lattice_utils import ASSET_KEYS  # nopycln: import
from .db_interfaces.lattice_utils import METADATA_KEYS  # nopycln: import
from .db_interfaces.lattice_utils import _meta_record_map, _to_meta
from .tg import ELECTRON_KEYS, get_compute_graph

LATTICE_KEYS = list(_meta_record_map.keys())


class Lattice(DispatchedObject):
    model = models.Lattice
    asset_link_model = models.LatticeAsset

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
        self._metadata = _to_meta(session, record, keys)
        self._assets = {}
        self._record = record

        self._lattice_id = self._record.id

        self.transport_graph = get_compute_graph(self._lattice_id, bare, keys=electron_keys)

    @property
    def keys(self) -> List:
        return self._keys

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, meta: Dict):
        self._metadata = meta

    @property
    def assets(self):
        return self._assets

    @classmethod
    def meta_record_map(cls: DispatchedObject, key: str) -> str:
        return _meta_record_map[key]

    def _to_meta(self, session: Session, record: models.Lattice, keys: List):
        return _to_meta(session, record, keys)

    @property
    def __name__(self):
        return self.get_value("__name__")

    @property
    def workflow_function(self):
        return self.get_value("workflow_function")
