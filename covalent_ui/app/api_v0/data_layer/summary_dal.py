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

from sqlite3 import InterfaceError
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.sql import desc, func, or_

from covalent_ui.app.api_v0.database.schema.lattices_schema import Lattice
from covalent_ui.app.api_v0.models.dispatch_model import (
    DeleteDispatchesRequest,
    DeleteDispatchesResponse,
    DispatchDashBoardResponse,
    DispatchResponse,
    SortDirection,
)


class Summary:
    """Summery data access layer"""

    def __init__(self, db_con: Session) -> None:
        self.db_con = db_con

    def get_summary(self, count, offset, sort_by, search, sort_direction) -> List[Lattice]:
        """
        Get summary of top most lattices
        Args:
            req.count: number of rows to be selected
            req.offset: number rows to be skipped
            req.sort_by: sort by field name(run_time, status, started, lattice)
            req.search: search by text
            req.direction: sort by direction ASE, DESC
        Return:
            List of top most Lattices and count
        """
        counter = 0
        if search is None:
            counter = self.db_con.query(func.count(Lattice.id)).filter(
                Lattice.electron_id.is_(None)
            )
            search = ""
        data = (
            self.db_con.query(
                Lattice.dispatch_id.label("dispatch_id"),
                Lattice.name.label("lattice_name"),
                (
                    func.strftime("%s", Lattice.completed_at)
                    - func.strftime("%s", Lattice.started_at)
                ).label("runtime"),
                Lattice.created_at.label("started_at"),
                Lattice.updated_at.label("ended_at"),
                Lattice.status.label("status"),
            )
            .filter(
                or_(
                    Lattice.name.ilike(f"%{search}%"),
                    Lattice.dispatch_id.ilike(f"%{search}%"),
                ),
                Lattice.electron_id.is_(None),
            )
            .order_by(
                desc(sort_by.value)
                if sort_direction == SortDirection.DESCENDING
                else sort_by.value
            )
            .offset(offset)
            .limit(count)
            .all()
        )

        # count = self.db_con.query(func.count(Lattice.id)).filter(Lattice.electron_id.is_(None))
        counter = len(data)
        return DispatchResponse(items=data, count=counter)

    def get_summary_overview(self) -> Lattice:
        """
        Get summary overview
        Args:
            None
        Return:
            Total jobs running,
            Total jobs done,
            Latest running task status,
            Total dispatcher duration
        """
        query1 = self.db_con.query((func.count(Lattice.id)).label("total_jobs_running")).first()
        query2 = self.db_con.query(
            (func.count(Lattice.id))
            .filter(Lattice.status == "RUNNING")
            .label("total_jobs_running")
        ).first()
        query3 = self.db_con.query(
            (func.count(Lattice.id)).filter(Lattice.status == "COMPLETED").label("total_jobs_done")
        ).first()
        query4 = self.db_con.query(
            (func.count(Lattice.id)).filter(Lattice.status == "FAILED").label("total_jobs_failed")
        ).first()
        query5 = self.db_con.query(Lattice.status).order_by(Lattice.updated_at.desc()).first()
        query5 = self.db_con.query(
            (func.count(Lattice.id)).filter(Lattice.status == "FAILED").label("total_failed")
        ).first()
        return DispatchDashBoardResponse(
            total_jobs_running=query1[0],
            total_jobs_completed=query2[0],
            latest_running_task_status=query3[0],
            total_dispatcher_duration=query4[0] * 1000,
            total_jobs_failed=query5[0],
            total_jobs=query1[0] + query2[0] + query5[0],
        )

    def delete_dispatches(self, req: DeleteDispatchesRequest) -> Lattice:
        """
        Delete dispatches
        Args:
            List[dispatch_id]
        Return:
            list of status(i.e whether given dispatch id is deleted successfully or failed)
        """
        success = []
        failure = []
        for dispatch_id in req.dispatches:
            try:
                data = (
                    self.db_con.query(Lattice)
                    .filter(Lattice.dispatch_id == str(dispatch_id))
                    .first()
                )
                if data is not None:
                    self.db_con.delete(data)
                    self.db_con.commit()
                    success.append(dispatch_id)
                else:
                    failure.append(dispatch_id)
            except InterfaceError:
                failure.append(dispatch_id)

        if len(failure) > 0:
            message = "Some of the dispatches could not be deleted. Pls try again!"
        else:
            message = f"All {len(req.dispatches)} deleted successfully"
        return DeleteDispatchesResponse(
            success_items=success,
            failure_items=failure,
            message=message,
        )
