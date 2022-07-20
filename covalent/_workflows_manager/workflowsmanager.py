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

from sqlalchemy import select

from .._data_store import DataStore, models
from .._results_manager.result import Result
from .._shared_files.config import get_config


def save_result(data_store: DataStore, result_object: Result):
    dispatch_id = result_object.dispatch_id

    update = False
    stmt = select(models.Lattice.dispatch_id).where(models.Lattice.dispatch_id == dispatch_id)
    with data_store.begin_session() as ds:
        row = ds.db_session.execute(stmt).first()
    if row:
        update = True

    metadata = {"dispatch_id": dispatch_id}
    with data_store.begin_session(metadata) as session:
        result_object.persist(session, update)


def load_result(data_store: DataStore, dispatch_id: str) -> Result:
    raise NotImplementedError
