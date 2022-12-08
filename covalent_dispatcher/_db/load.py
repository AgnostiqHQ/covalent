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

from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from covalent._shared_files import logger

from .datastore import workflow_db
from .models import Electron, Lattice

app_log = logger.app_log
log_stack_info = logger.log_stack_info


def _node_records(session: Session, dispatch_id: str) -> List[Electron]:
    stmt = (
        select(Electron)
        .join(Lattice, Lattice.id == Electron.parent_lattice_id)
        .where(Lattice.dispatch_id == dispatch_id)
    )
    records = session.execute(stmt).all()
    return list(map(lambda r: r.Electron, records))


# includes virtual "-1" node
def task_job_map(dispatch_id: str) -> dict:
    with workflow_db.Session() as session:
        e_records = _node_records(session, dispatch_id)
        return {e.transport_graph_node_id: e.job_id for e in e_records}
