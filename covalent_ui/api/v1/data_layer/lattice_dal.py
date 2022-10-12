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

"""Lattice Data Layer"""

from datetime import timezone
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.sql import desc, func

from covalent_ui.api.v1.database.schema.lattices import Lattice
from covalent_ui.api.v1.models.dispatch_model import SortDirection
from covalent_ui.api.v1.models.lattices_model import LatticeDetailResponse


class Lattices:
    """Lattice data access layer"""

    def __init__(self, db_con: Session) -> None:
        self.db_con = db_con

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
                func.datetime(Lattice.started_at, "localtime").label("start_time"),
                func.IFNULL(func.datetime(Lattice.completed_at, "localtime"), None).label(
                    "end_time"
                ),
                Lattice.electron_num.label("total_electrons"),
                Lattice.completed_electron_num.label("total_electrons_completed"),
                (
                    (
                        func.strftime(
                            "%s",
                            func.IFNULL(Lattice.completed_at, func.datetime.now(timezone.utc)),
                        )
                        - func.strftime("%s", Lattice.started_at)
                    )
                    * 1000
                ).label("runtime"),
                func.IFNULL(func.datetime(Lattice.updated_at, "localtime"), None).label(
                    "updated_at"
                ),
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
                Lattice.executor_data_filename,
                Lattice.workflow_executor,
                Lattice.workflow_executor_data_filename,
                Lattice.error_filename,
                Lattice.inputs_filename,
                Lattice.results_filename,
                Lattice.storage_type,
                Lattice.function_filename,
                Lattice.transport_graph_filename,
                Lattice.started_at.label("started_at"),
                Lattice.completed_at.label("ended_at"),
                Lattice.electron_num.label("total_electrons"),
                Lattice.completed_electron_num.label("total_electrons_completed"),
            )
            .filter(Lattice.dispatch_id == str(dispatch_id), Lattice.is_active.is_not(False))
            .first()
        )

    def get_lattice_id_by_dispatch_id(self, dispatch_id: UUID):
        """
        Get top lattice id from dispatch id
        Args:
            dispatch_id: UUID of dispatch
        Returns:
            Top most lattice id
        """
        data = (
            self.db_con.query(Lattice.id)
            .filter(Lattice.dispatch_id == str(dispatch_id), Lattice.electron_id.is_(None))
            .first()
        )
        return data[0]

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
                        func.strftime(
                            "%s",
                            func.IFNULL(Lattice.completed_at, func.datetime.now(timezone.utc)),
                        )
                        - func.strftime("%s", Lattice.started_at)
                    )
                    * 1000
                ).label("runtime"),
                Lattice.electron_num.label("total_electrons"),
                Lattice.completed_electron_num.label("total_electrons_completed"),
                Lattice.status.label("status"),
                func.datetime(Lattice.started_at, "localtime").label("started_at"),
                func.IFNULL(func.datetime(Lattice.completed_at, "localtime"), None).label(
                    "ended_at"
                ),
                func.datetime(Lattice.updated_at, "localtime").label("updated_at"),
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
