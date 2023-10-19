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

"""Lattice Data Layer"""

from typing import List
from uuid import UUID

from sqlalchemy import extract, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import desc, func

from covalent_ui.api.v1.database.schema.lattices import Lattice
from covalent_ui.api.v1.models.dispatch_model import SortDirection
from covalent_ui.api.v1.models.lattices_model import LatticeDetailResponse


class Lattices:
    """Lattice data access layer"""

    def __init__(self, db_con: Session) -> None:
        self.db_con = db_con

    def dispatch_exist(self, dispatch_id: UUID) -> bool:
        return self.db_con.execute(
            select(Lattice).where(Lattice.dispatch_id == str(dispatch_id))
        ).fetchone()

    def get_lattices_id(self, dispatch_id: UUID) -> LatticeDetailResponse:
        """
        Get lattices from dispatch id
        Args:
            dispatch_id: Refers to the dispatch_id in lattices table
        Return:
            Top most lattice with the given dispatch_id
            (i.e lattice with the same dispatch_id, but electron_id as null)
        """

        return (
            self.db_con.query(
                Lattice.dispatch_id,
                Lattice.status,
                Lattice.storage_path.label("directory"),
                Lattice.error_filename,
                Lattice.results_filename,
                Lattice.docstring_filename,
                Lattice.started_at.label("start_time"),
                func.coalesce((Lattice.completed_at), None).label("end_time"),
                Lattice.electron_num.label("total_electrons"),
                Lattice.completed_electron_num.label("total_electrons_completed"),
                (
                    (
                        func.coalesce(
                            extract("epoch", Lattice.completed_at),
                            extract("epoch", func.now()),
                        )
                        - extract("epoch", Lattice.started_at)
                    )
                    * 1000
                ).label("runtime"),
                func.coalesce((Lattice.updated_at), None).label("updated_at"),
            )
            .filter(Lattice.dispatch_id == str(dispatch_id), Lattice.is_active.is_not(False))
            .first()
        )

    def get_lattices_id_storage_file(self, dispatch_id: UUID):
        """
        Get storage file name
        Args:
            dispatch_id: Refers to the dispatch_id in lattices table
        Return:
            Top most lattice with the given dispatch_id along with file names
            (i.e lattice with the same dispatch_id, but electron_id as null)
        """

        return (
            self.db_con.query(
                Lattice.dispatch_id,
                Lattice.status,
                Lattice.storage_path.label("directory"),
                Lattice.error_filename,
                Lattice.function_string_filename,
                Lattice.executor,
                Lattice.executor_data,
                Lattice.workflow_executor,
                Lattice.workflow_executor_data,
                Lattice.error_filename,
                Lattice.inputs_filename,
                Lattice.results_filename,
                Lattice.storage_type,
                Lattice.function_filename,
                Lattice.started_at.label("started_at"),
                Lattice.completed_at.label("ended_at"),
                Lattice.electron_num.label("total_electrons"),
                Lattice.completed_electron_num.label("total_electrons_completed"),
            )
            .filter(Lattice.dispatch_id == str(dispatch_id), Lattice.is_active.is_not(False))
            .first()
        )

    def get_sub_lattice_details(self, sort_by, sort_direction, dispatch_id) -> List[Lattice]:
        """
        Get summary of sub lattices
        Args:
            req.sort_by: sort by field name(run_time, status, lattice_name)
            req.direction: sort by direction ASE, DESC
        Return:
            List of sub Lattices
        """

        data = (
            self.db_con.query(
                Lattice.dispatch_id.label("dispatch_id"),
                Lattice.name.label("lattice_name"),
                (
                    (
                        func.coalesce(
                            extract("epoch", Lattice.completed_at), extract("epoch", func.now())
                        )
                        - extract("epoch", Lattice.started_at)
                    )
                    * 1000
                ).label("runtime"),
                Lattice.electron_num.label("total_electrons"),
                Lattice.completed_electron_num.label("total_electrons_completed"),
                Lattice.status.label("status"),
                Lattice.started_at.label("started_at"),
                func.coalesce((Lattice.completed_at), None).label("ended_at"),
                Lattice.updated_at.label("updated_at"),
            )
            .filter(
                Lattice.is_active.is_not(False),
                Lattice.electron_id.is_not(None),
                Lattice.root_dispatch_id == str(dispatch_id),
            )
            .order_by(
                desc(sort_by.value)
                if sort_direction == SortDirection.DESCENDING
                else sort_by.value
            )
            .all()
        )

        return data
