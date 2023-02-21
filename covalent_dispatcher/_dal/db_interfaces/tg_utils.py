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

"""Mappings between graph attributes and DB records"""


from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..._db.models import Electron as ElectronRecord
from ..._db.models import ElectronDependency as EdgeRecord
from ..._db.models import Lattice as LatticeRecord


def _node_record(session: Session, lattice_id: int, node_id: int) -> ElectronRecord:

    stmt = (
        select(ElectronRecord)
        .where(ElectronRecord.parent_lattice_id == lattice_id)
        .where(ElectronRecord.transport_graph_node_id == node_id)
    )
    record = session.execute(stmt).first()
    if not record:
        raise KeyError(f"Invalid Node id {node_id} for lattice record {lattice_id}")

    return record[0]


def _node_records(session: Session, lattice_id: int, node_ids: List[int]) -> List[ElectronRecord]:

    stmt = select(ElectronRecord).where(ElectronRecord.parent_lattice_id == lattice_id)
    if len(node_ids) > 0:
        stmt = stmt.where(ElectronRecord.transport_graph_node_id.in_(node_ids))
    records = session.execute(stmt).all()
    if len(records) < len(node_ids):
        raise KeyError(f"Invalid Node ids {node_ids} for lattice record {lattice_id}")
    return list(map(lambda r: r.Electron, records))


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


def _incoming_edge_records(session: Session, electron_id: int) -> List[ElectronRecord]:
    stmt = (
        select(ElectronRecord, EdgeRecord)
        .join(EdgeRecord, EdgeRecord.parent_electron_id == ElectronRecord.id)
        .where(EdgeRecord.electron_id == electron_id)
    )
    records = session.execute(stmt).all()
    return list(map(lambda r: (r.Electron, r.ElectronDependency), records))


def _child_records(session: Session, electron_id: int) -> List[ElectronRecord]:
    stmt = (
        select(ElectronRecord)
        .join(EdgeRecord, EdgeRecord.electron_id == ElectronRecord.id)
        .where(EdgeRecord.parent_electron_id == electron_id)
    )
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
