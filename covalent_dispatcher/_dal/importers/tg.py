# Copyright 2023 Agnostiq Inc.
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


"""Functions to transform ResultSchema -> Result"""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from covalent._shared_files import logger
from covalent._shared_files.schemas.edge import EdgeSchema
from covalent._shared_files.schemas.transport_graph import TransportGraphSchema
from covalent_dispatcher._dal.edge import ElectronDependency
from covalent_dispatcher._dal.electron import Electron
from covalent_dispatcher._dal.job import Job
from covalent_dispatcher._dal.lattice import Lattice
from covalent_dispatcher._db import models
from covalent_dispatcher._object_store.base import BaseProvider

from .electron import import_electron

app_log = logger.app_log


def import_transport_graph(
    session: Session,
    dispatch_id: str,
    tg: TransportGraphSchema,
    lat: Lattice,
    object_store: BaseProvider,
    electron_id: Optional[int],
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

    gid_job_record_map = {}

    # Maps node ids to asset record dictionaries
    electron_asset_links = {}

    for gid in task_groups:
        # Create a job record for each task group
        job_kwargs = {
            "cancel_requested": cancel_requested,
        }

        gid_job_record_map[gid] = Job.create(session, insert_kwargs=job_kwargs, flush=False)

    # Write job records to DB and retrieve primary keys

    session.flush()

    for gid, node_group in task_groups.items():
        for node in node_group:
            job_record = gid_job_record_map[gid]
            e_record, asset_records_by_key, node = import_electron(
                session,
                dispatch_id,
                node,
                lat,
                object_store,
                job_id=job_record.id,
            )
            output_nodes.append(node)
            electron_map[node.id] = e_record
            electron_asset_links[node.id] = asset_records_by_key

    # Compute asset ids, electron ids, and create associations

    n_records = len(electron_map)
    st = datetime.now()
    session.flush()
    et = datetime.now()
    delta = (et - st).total_seconds()
    app_log.debug(f"Inserting {n_records} electron records took {delta} seconds")

    n_records = sum(
        len(asset_records_by_key) for asset_records_by_key in electron_asset_links.values()
    )

    st = datetime.now()
    session.flush()
    et = datetime.now()
    delta = (et - st).total_seconds()
    app_log.debug(f"Inserting {n_records} asset records took {delta} seconds")

    meta_asset_associations = []
    for node_id, asset_records in electron_asset_links.items():
        electron_dal = Electron(session, electron_map[node_id])
        meta_asset_associations.extend(
            electron_dal.associate_asset(session, key, asset_rec.id)
            for key, asset_rec in asset_records.items()
        )
    n_records = len(meta_asset_associations)

    st = datetime.now()
    session.flush()
    et = datetime.now()
    delta = (et - st).total_seconds()
    app_log.debug(f"Inserting {n_records} asset record links took {delta} seconds")

    # Insert edges
    edge_records = []
    edges = [_import_edge(session, e, electron_map, edge_records) for e in tg.links]

    n_records = 0
    n_records = len(edge_records)

    st = datetime.now()
    session.flush()
    et = datetime.now()
    delta = (et - st).total_seconds()
    app_log.debug(f"Inserting {n_records} edge records took {delta} seconds")

    return TransportGraphSchema(nodes=output_nodes, links=edges)


def _import_edge(
    session: Session,
    edge: EdgeSchema,
    electron_map: Dict[int, models.Electron],
    edge_records: List[models.ElectronDependency],
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

    edge_records.append(
        ElectronDependency.create(session, insert_kwargs=insert_kwargs, flush=False)
    )

    # No filtering involved
    return edge
