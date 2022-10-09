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

import uuid
from datetime import datetime, timezone
from sqlite3 import InterfaceError
from typing import List

from sqlalchemy import case, update
from sqlalchemy.orm import Session
from sqlalchemy.sql import desc, func, or_
from sqlalchemy.util import immutabledict

from covalent_dispatcher._db.models import ElectronDependency
from covalent_ui.api.v1.database.schema.electron import Electron
from covalent_ui.api.v1.database.schema.lattices import Lattice
from covalent_ui.api.v1.models.dispatch_model import (
    DeleteAllDispatchesRequest,
    DeleteDispatchesRequest,
    DeleteDispatchesResponse,
    DispatchDashBoardResponse,
    DispatchResponse,
    SortDirection,
)
from covalent_ui.api.v1.utils.status import Status


class Summary:
    """Summery data access layer"""

    def __init__(self, db_con: Session) -> None:
        self.db_con = db_con

    def get_summary(
        self, count, offset, sort_by, search, sort_direction, status_filter
    ) -> List[Lattice]:
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
        result = None

        status_filters = self.get_filters(status_filter)

        data = self.db_con.query(
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
            func.datetime(Lattice.started_at, "localtime").label("started_at"),
            func.IFNULL(func.datetime(Lattice.completed_at, "localtime"), None).label("ended_at"),
            Lattice.status.label("status"),
            func.datetime(Lattice.updated_at, "localtime").label("updated_at"),
        ).filter(
            or_(
                Lattice.name.ilike(f"%{search}%"),
                Lattice.dispatch_id.ilike(f"%{search}%"),
            ),
            Lattice.status.in_(status_filters),
            Lattice.is_active.is_not(False),
        )

        if sort_by.value == "status":
            case_status = case(
                [
                    (Lattice.status == Status.NEW_OBJECT.value, 0),
                    (Lattice.status == Status.RUNNING.value, 1),
                    (Lattice.status == Status.COMPLETED.value, 2),
                    (Lattice.status == Status.POSTPROCESSING.value, 3),
                    (Lattice.status == Status.POSTPROCESSING_FAILED.value, 4),
                    (Lattice.status == Status.PENDING_POSTPROCESSING.value, 5),
                    (Lattice.status == Status.FAILED.value, 6),
                    (Lattice.status == Status.CANCELLED.value, 7),
                ]
            )
            data = data.order_by(
                desc(case_status) if sort_direction == SortDirection.DESCENDING else case_status
            )
        else:
            data = data.order_by(
                desc(sort_by.value)
                if sort_direction == SortDirection.DESCENDING
                else sort_by.value
            )

        result = data.offset(offset).limit(count).all()

        counter = (
            self.db_con.query(func.count(Lattice.id))
            .filter(
                or_(
                    Lattice.name.ilike(f"%{search}%"),
                    Lattice.dispatch_id.ilike(f"%{search}%"),
                ),
                Lattice.status.in_(status_filters),
                Lattice.is_active.is_not(False),
            )
            .first()
        )
        return DispatchResponse(items=result, total_count=counter[0])

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

        total_jobs_running = self.db_con.query(
            (func.count(Lattice.id))
            .filter(
                Lattice.status == "RUNNING",
                Lattice.is_active.is_not(False),
            )
            .label("total_jobs_running")
        ).first()

        total_jobs_done = self.db_con.query(
            (func.count(Lattice.id))
            .filter(
                or_(
                    Lattice.status == "COMPLETED",
                    Lattice.status == "POSTPROCESSING",
                    Lattice.status == "POSTPROCESSING_FAILED",
                    Lattice.status == "PENDING_POSTPROCESSING",
                ),
                Lattice.is_active.is_not(False),
            )
            .label("total_jobs_done")
        ).first()

        last_ran_job_status = (
            self.db_con.query(Lattice.status)
            .filter(Lattice.is_active.is_not(False))
            .order_by(Lattice.updated_at.desc())
            .first()
        )

        run_time = (
            self.db_con.query(
                (
                    func.sum(
                        func.strftime("%s", Lattice.completed_at)
                        - func.strftime("%s", Lattice.started_at)
                    )
                    * 1000
                ).label("run_time")
            )
            .filter(Lattice.is_active.is_not(False))
            .first()
        )

        total_failed = self.db_con.query(
            (func.count(Lattice.id))
            .filter(
                Lattice.status == "FAILED",
                Lattice.is_active.is_not(False),
            )
            .label("total_jobs_failed")
        ).first()

        total_jobs = self.db_con.query(
            (func.count(Lattice.id)).filter(Lattice.is_active.is_not(False)).label("total_jobs")
        ).first()

        total_jobs_cancelled = self.db_con.query(
            (func.count(Lattice.id))
            .filter(
                Lattice.status == "CANCELLED",
                Lattice.is_active.is_not(False),
            )
            .label("total_jobs_cancelled")
        ).first()

        total_jobs_new_object = self.db_con.query(
            (func.count(Lattice.id))
            .filter(
                Lattice.status == "NEW_OBJECT",
                Lattice.is_active.is_not(False),
            )
            .label("total_jobs_new_object")
        ).first()

        run_time = 0 if run_time is None else run_time
        return DispatchDashBoardResponse(
            total_jobs_running=total_jobs_running[0],
            total_jobs_completed=total_jobs_done[0],
            latest_running_task_status=last_ran_job_status[0]
            if last_ran_job_status is not None
            else None,
            total_dispatcher_duration=run_time[0] if run_time is not None else 0,
            total_jobs_failed=total_failed[0],
            total_jobs_cancelled=total_jobs_cancelled[0],
            total_jobs_new_object=total_jobs_new_object[0],
            total_jobs=total_jobs[0],
        )

    def delete_dispatches(self, data: DeleteDispatchesRequest):
        """
        Delete dispatches
        Args:
            List[dispatch_id]
        Return:
            list of status(i.e whether given dispatch id is deleted successfully or failed)
        """
        success = []
        failure = []
        message = "No dispatches were deleted"
        if len(data.dispatches) == 0:
            return DeleteDispatchesResponse(
                success_items=success,
                failure_items=failure,
                message=message,
            )
        for dispatch_id in data.dispatches:
            try:
                lattice_id = (
                    self.db_con.query(Lattice.id)
                    .filter(
                        Lattice.dispatch_id == str(dispatch_id),
                        Lattice.is_active.is_not(False),
                    )
                    .first()
                )
                if lattice_id is None:
                    failure.append(dispatch_id)
                    continue
                electron_ids = (
                    self.db_con.query(Electron.id)
                    .filter(
                        Electron.parent_lattice_id == lattice_id[0],
                        Electron.is_active.is_not(False),
                    )
                    .scalar_subquery()
                )

                update_electron_dependency = (
                    update(ElectronDependency)
                    .where(ElectronDependency.parent_electron_id.in_(electron_ids))
                    .values(
                        {
                            ElectronDependency.updated_at: datetime.now(timezone.utc),
                            ElectronDependency.is_active: False,
                        }
                    )
                )
                self.db_con.execute(
                    update_electron_dependency,
                    execution_options=immutabledict({"synchronize_session": "fetch"}),
                )
                update_electron = (
                    update(Electron)
                    .where(Electron.parent_lattice_id == lattice_id[0])
                    .values(
                        {
                            Electron.updated_at: datetime.now(timezone.utc),
                            Electron.is_active: False,
                        }
                    )
                )
                self.db_con.execute(update_electron)

                update_lattice = (
                    update(Lattice)
                    .where(Lattice.id == lattice_id[0])
                    .values(
                        {
                            Lattice.updated_at: datetime.now(timezone.utc),
                            Lattice.is_active: False,
                        }
                    )
                )
                self.db_con.execute(update_lattice)
                self.db_con.commit()
                success.append(dispatch_id)
            except InterfaceError:
                failure.append(dispatch_id)
        if len(success) > 0:
            message = "Dispatch(es) have been deleted successfully!"
            if len(failure) > 0:
                message = "Some of the dispatches could not be deleted"

        return DeleteDispatchesResponse(
            success_items=success,
            failure_items=failure,
            message=message,
        )

    def delete_all_dispatches(self, data: DeleteAllDispatchesRequest):
        """
        Delete dispatches
        Args:
            List[dispatch_id]
        Return:
            list of status(i.e whether given dispatch id is deleted successfully or failed)
        """
        success = []
        failure = []
        status_filters = self.get_filters(data.status_filter)
        filter_dispatches = (
            self.db_con.query(Lattice.id, Lattice.dispatch_id)
            .filter(
                or_(
                    Lattice.name.ilike(f"%{data.search_string}%"),
                    Lattice.dispatch_id.ilike(f"%{data.search_string}%"),
                ),
                Lattice.status.in_(status_filters),
                Lattice.is_active.is_not(False),
            )
            .all()
        )
        dispatch_ids = [o.id for o in filter_dispatches]
        dispatches = [uuid.UUID(o.dispatch_id) for o in filter_dispatches]
        if len(dispatches) >= 1:
            try:
                electron_ids = (
                    self.db_con.query(Electron.id)
                    .filter(
                        Electron.parent_lattice_id.in_(dispatch_ids),
                        Electron.is_active.is_not(False),
                    )
                    .scalar_subquery()
                )

                update_electron_dependency = (
                    update(ElectronDependency)
                    .where(ElectronDependency.parent_electron_id.in_(electron_ids))
                    .values(
                        {
                            ElectronDependency.updated_at: datetime.now(timezone.utc),
                            ElectronDependency.is_active: False,
                        }
                    )
                )
                update_electron = (
                    update(Electron)
                    .where(Electron.id.in_(electron_ids))
                    .values(
                        {
                            Electron.updated_at: datetime.now(timezone.utc),
                            Electron.is_active: False,
                        }
                    )
                )
                update_lattice = (
                    update(Lattice)
                    .where(Lattice.id.in_(dispatch_ids))
                    .values(
                        {
                            Lattice.updated_at: datetime.now(timezone.utc),
                            Lattice.is_active: False,
                        }
                    )
                )
                self.db_con.execute(
                    update_electron_dependency,
                    execution_options=immutabledict({"synchronize_session": "fetch"}),
                )
                self.db_con.execute(
                    update_electron,
                    execution_options=immutabledict({"synchronize_session": "fetch"}),
                )
                self.db_con.execute(
                    update_lattice,
                    execution_options=immutabledict({"synchronize_session": "fetch"}),
                )
                self.db_con.commit()
                success = dispatches
            except InterfaceError:
                failure = dispatches
        if (len(failure) == 0 and len(success) == 0) or (len(failure) > 0 and len(success) == 0):
            message = "No dispatches were deleted"
        elif len(failure) > 0 and len(success) > 0:
            message = "Some of the dispatches could not be deleted"
        else:
            message = "Dispatch(es) have been deleted successfully!"
        return DeleteDispatchesResponse(
            success_items=success,
            failure_items=failure,
            message=message,
        )

    def get_filters(self, status_filter: Status):
        filters = []
        if status_filter == Status.ALL:
            filters = [status.value for status in Status]
        elif status_filter == Status.COMPLETED:
            filters.append(Status.COMPLETED.value)
            filters.append(Status.POSTPROCESSING.value)
            filters.append(Status.POSTPROCESSING_FAILED.value)
            filters.append(Status.PENDING_POSTPROCESSING.value)
        else:
            filters = [status_filter.value]

        return filters
