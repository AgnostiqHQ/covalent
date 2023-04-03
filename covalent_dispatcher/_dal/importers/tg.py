# Copyright 2023 Agnostiq Inc.
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


"""Functions to transform ResultSchema -> Result"""

import os
from typing import Dict, Optional

from sqlalchemy.orm import Session

from covalent._shared_files import logger
from covalent._shared_files.schemas.edge import EdgeSchema
from covalent._shared_files.schemas.transport_graph import TransportGraphSchema
from covalent_dispatcher._dal.edge import ElectronDependency
from covalent_dispatcher._dal.electron import Electron
from covalent_dispatcher._dal.job import Job
from covalent_dispatcher._dal.lattice import Lattice
from covalent_dispatcher._db import models

from .electron import import_electron

app_log = logger.app_log


def import_transport_graph(
    session: Session,
    tg: TransportGraphSchema,
    lat: Lattice,
    storage_path: str,
    electron_id: Optional[int],
    data_uri_prefix: str,
) -> TransportGraphSchema:
    electron_map = {}
    output_nodes = []

    # Propagate parent electron id's `cancel_requested` property to the sublattice electrons
    if electron_id is not None:
        parent_e_record = Electron.meta_type.get_by_primary_key(session, electron_id)
        job_record = Job.get_by_primary_key(session=session, primary_key=parent_e_record.job_id)
        cancel_requested = job_record.cancel_requested
    else:
        cancel_requested = False

    # Gather nodes into task groups
    task_groups = {i: [] for i in range(len(tg.nodes))}
    for node in tg.nodes:
        gid = node.metadata.task_group_id
        task_groups[gid].append(node)

    gids = {k: list(map(lambda n: n.id, v)) for k, v in task_groups.items()}

    for gid, node_group in task_groups.items():
        # Create a job record for each task group
        job_kwargs = {
            "cancel_requested": cancel_requested,
        }

        job_record = Job.insert(session, insert_kwargs=job_kwargs, flush=True)

        for node in node_group:
            node_storage_path = os.path.join(storage_path, f"node_{node.id}")
            os.makedirs(node_storage_path)
            node_data_uri_prefix = data_uri_prefix + f"/{node.id}"
            e_record, node = import_electron(
                session,
                node,
                lat,
                node_storage_path,
                job_id=job_record.id,
                data_uri_prefix=node_data_uri_prefix,
            )
            output_nodes.append(node)
            electron_map[node.id] = e_record

    edges = [_import_edge(session, e, electron_map) for e in tg.links]

    return TransportGraphSchema(nodes=output_nodes, links=edges)


def _import_edge(
    session: Session, edge: EdgeSchema, electron_map: Dict[int, models.Electron]
) -> EdgeSchema:
    source_electron = electron_map[edge.source]
    target_electron = electron_map[edge.target]
    edge_name = edge.metadata.edge_name
    param_type = edge.metadata.param_type
    arg_index = edge.metadata.arg_index
    insert_kwargs = {
        "electron_id": target_electron.id,
        "parent_electron_id": source_electron.id,
        "edge_name": edge_name,
        "parameter_type": param_type,
        "arg_index": arg_index,
    }

    ElectronDependency.insert(session, insert_kwargs=insert_kwargs, flush=False)

    # No filtering involved
    return edge
