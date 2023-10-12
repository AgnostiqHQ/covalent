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

"""Mappings between graph attributes and DB records"""


from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Load, Session

from ..._db.models import Electron as ElectronRecord
from ..._db.models import ElectronDependency as EdgeRecord
from ..._db.models import Lattice as LatticeRecord
from .. import electron


def _edge_records_for_nodes(
    session: Session, parent_electron_id: int, child_electron_id: int
) -> List[EdgeRecord]:
    stmt = (
        select(EdgeRecord)
        .where(EdgeRecord.electron_id == child_electron_id)
        .where(EdgeRecord.parent_electron_id == parent_electron_id)
    )
    records = session.scalars(stmt).all()
    if not records:
        raise KeyError(f"No edges between nodes {parent_electron_id}, {child_electron_id}")
    return list(records)


def _incoming_edge_records(
    session: Session, electron_id: int, *, keys: List
) -> List[ElectronRecord]:
    stmt = (
        select(ElectronRecord, EdgeRecord)
        .join(EdgeRecord, EdgeRecord.parent_electron_id == ElectronRecord.id)
        .where(EdgeRecord.electron_id == electron_id)
    )
    if len(keys) > 0:
        fields = list(map(electron.Electron.meta_record_map, keys))
        attrs = [getattr(ElectronRecord, f) for f in fields]
        stmt = stmt.options(Load(ElectronRecord).load_only(*attrs))

    records = session.execute(stmt).all()
    return list(map(lambda r: (r.Electron, r.ElectronDependency), records))


def _child_records(session: Session, electron_id: int, *, keys: List) -> List[ElectronRecord]:
    stmt = (
        select(ElectronRecord)
        .join(EdgeRecord, EdgeRecord.electron_id == ElectronRecord.id)
        .where(EdgeRecord.parent_electron_id == electron_id)
    )
    if len(keys) > 0:
        fields = list(map(electron.Electron.meta_record_map, keys))
        attrs = [getattr(ElectronRecord, f) for f in fields]
        stmt = stmt.options(Load(ElectronRecord).load_only(*attrs))

    records = session.execute(stmt).all()
    return list(map(lambda r: r.Electron, records))


# Join electron dependency with filtered electrons on destination electron
def _all_edge_records(session: Session, lattice_id: int) -> List[EdgeRecord]:
    stmt = (
        select(EdgeRecord)
        .join(ElectronRecord, ElectronRecord.id == EdgeRecord.electron_id)
        .join(LatticeRecord, LatticeRecord.id == ElectronRecord.parent_lattice_id)
        .where(LatticeRecord.id == lattice_id)
    )
    records = session.execute(stmt).all()
    return list(map(lambda r: r.ElectronDependency, records))
