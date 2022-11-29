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

"""This module rehydrates a transport graph from the db"""

import json
from typing import Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from covalent._shared_files import logger
from covalent._workflow.transport import _TransportGraph

from .datastore import workflow_db
from .models import Electron, ElectronDependency, Lattice

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class MissingElectronRecordError(Exception):
    pass


def _node_records(session: Session, dispatch_id: str) -> List[Electron]:
    stmt = (
        select(Electron)
        .join(Lattice, Lattice.id == Electron.parent_lattice_id)
        .where(Lattice.dispatch_id == dispatch_id)
    )
    records = session.execute(stmt).all()
    return list(map(lambda r: r.Electron, records))


# Join electron dependency with filtered electrons on destination electron
def _edge_records(session: Session, dispatch_id: str) -> List[ElectronDependency]:
    stmt = (
        select(ElectronDependency)
        .join(Electron, Electron.id == ElectronDependency.electron_id)
        .join(Lattice, Lattice.id == Electron.parent_lattice_id)
        .where(Lattice.dispatch_id == dispatch_id)
    )
    records = session.execute(stmt).all()
    return list(map(lambda r: r.ElectronDependency, records))


def _to_abstract_node(e_record: Electron) -> Tuple[int, Dict]:
    node_id = e_record.transport_graph_node_id
    attrs = {
        "uid": e_record.id,
        "type": e_record.type,
        "executor": e_record.executor,
        "executor_data": json.loads(e_record.executor_data),
        "job_id": e_record.job_id,
    }
    return node_id, attrs


def _to_abstract_edge(
    e_record: ElectronDependency, uid_node_id_map: Dict
) -> Tuple[int, int, Dict]:
    x = uid_node_id_map[e_record.parent_electron_id]
    y = uid_node_id_map[e_record.electron_id]
    attrs = {
        "edge_name": e_record.edge_name,
        "parameter_type": e_record.parameter_type,
        "arg_index": e_record.arg_index,
    }

    return x, y, attrs


def _abstract_nodes_and_edges(session: Session, dispatch_id: str):

    db_nodes = _node_records(session, dispatch_id)
    db_edges = _edge_records(session, dispatch_id)
    uid_nodeid_map = {e.id: e.transport_graph_node_id for e in db_nodes}
    nodes = list(map(_to_abstract_node, db_nodes))
    edges = list(map(lambda x: _to_abstract_edge(x, uid_nodeid_map), db_edges))

    return nodes, edges


def _make_transport_graph(nodes: List, edges: List) -> _TransportGraph:
    tg = _TransportGraph()
    for node in nodes:
        node_id, attrs = node
        tg.add_node_by_id(node_id, **attrs)
    for edge in edges:
        x, y, attrs = edge
        tg.add_edge(x, y, **attrs)
    return tg


def abstract_tg(dispatch_id: str) -> _TransportGraph:
    with workflow_db.Session() as session:
        nodes, edges = _abstract_nodes_and_edges(session, dispatch_id)
    return _make_transport_graph(nodes, edges)
