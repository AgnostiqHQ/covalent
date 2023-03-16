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
from .db_interfaces.lattice_utils import _get_asset_ids, _meta_record_map, _to_meta
from .tg import get_compute_graph


class Lattice(DispatchedObject):
    def __init__(
        self,
        session: Session,
        record: models.Lattice,
        bare: bool = False,
    ):
        metadata = _to_meta(session, record)

        self._metadata = metadata
        self._assets = {}
        self._record = record

        self._lattice_id = metadata["id"]

        self.transport_graph = get_compute_graph(self._lattice_id, bare)

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, meta: Dict):
        self._metadata = meta

    def get_asset_ids(self, session: Session, keys: List[str]) -> Dict[str, int]:
        return _get_asset_ids(session, self._lattice_id, keys)

    @property
    def assets(self):
        return self._assets

    def _get_db_record(self, session: Session) -> models.Lattice:
        record = session.query(models.Lattice).where(models.Lattice.id == self._lattice_id).first()
        return record

    def meta_record_map(self, key: str) -> str:
        return _meta_record_map[key]

    def _to_meta(self, session: Session, record):
        return _to_meta(session, record)

    @property
    def __name__(self):
        return self.get_value("__name__")

    @property
    def workflow_function(self):
        return self.get_value("workflow_function")
