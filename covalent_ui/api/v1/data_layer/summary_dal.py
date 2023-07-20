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
from typing import List

from sqlalchemy import case, extract, select, update
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
    DispatchModule,
    DispatchResponse,
    SortDirection,
)
from covalent_ui.api.v1.utils.status import Status


class Summary:
    """Summary data access layer"""

    def __init__(self, db_con: Session) -> None:
        self.db_con = db_con

    async def get_summary(
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
        status_filters = await self.get_filters(status_filter)
        select_query = [
            Lattice.dispatch_id.label("dispatch_id"),
            Lattice.name.label("lattice_name"),
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
            Lattice.electron_num.label("total_electrons"),
            Lattice.completed_electron_num.label("total_electrons_completed"),
            Lattice.started_at.label("started_at"),
            func.coalesce(Lattice.completed_at, None).label("ended_at"),
            Lattice.status.label("status"),
            Lattice.updated_at.label("updated_at"),
        ]
        where_query = [
            or_(
                Lattice.name.ilike(f"%{search}%"),
                Lattice.dispatch_id.ilike(f"%{search}%"),
            ),
            Lattice.status.in_(status_filters),
            Lattice.is_active.is_not(False),
            Lattice.electron_id.is_(None),
        ]
        order_by_query = []
        if sort_by.value == "status":
            case_status = case(
                (Lattice.status == Status.NEW_OBJECT.value, 0),
                (Lattice.status == Status.RUNNING.value, 1),
                (Lattice.status == Status.COMPLETED.value, 2),
                (Lattice.status == Status.POSTPROCESSING.value, 3),
                (Lattice.status == Status.POSTPROCESSING_FAILED.value, 4),
                (Lattice.status == Status.PENDING_POSTPROCESSING.value, 5),
                (Lattice.status == Status.FAILED.value, 6),
                (Lattice.status == Status.CANCELLED.value, 7),
            )
            order_by_query = [
                desc(case_status) if sort_direction == SortDirection.DESCENDING else case_status
            ]
        else:
            order_by_query = [
                desc(sort_by.value)
                if sort_direction == SortDirection.DESCENDING
                else sort_by.value
            ]
        orm_query = (
            select(*select_query)
            .where(*where_query)
            .order_by(*order_by_query)
            .slice(offset, count)
        )
        orm_query_counter = select(func.count()).where(*where_query)
        results = await self.db_con.execute(orm_query)
        counter = await self.db_con.scalar(orm_query_counter)
        return DispatchResponse(
            items=[DispatchModule.model_validate(result) for result in results],
            total_count=counter,
        )

    async def get_dispatch_count_by_status(
        self, status: str = "", is_active: bool = False, filter_by_job_done: bool = False
    ) -> int:
        filter_by = (
            [Lattice.status == status]
            if not filter_by_job_done
            else [
                or_(
                    Lattice.status == "COMPLETED",
                    Lattice.status == "POSTPROCESSING",
                    Lattice.status == "POSTPROCESSING_FAILED",
                    Lattice.status == "PENDING_POSTPROCESSING",
                )
            ]
        )
        filter_by.extend([Lattice.is_active.is_not(is_active), Lattice.electron_id.is_(None)])
        return await self.db_con.scalar(select(func.count()).where(*filter_by))

    async def get_summary_overview(self) -> DispatchDashBoardResponse:
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
        total_jobs_running = await self.get_dispatch_count_by_status(status="RUNNING")

        total_jobs_done = await self.get_dispatch_count_by_status(filter_by_job_done=True)

        last_ran_job_status = await self.db_con.scalar(
            select(Lattice.status)
            .filter(Lattice.is_active.is_not(False), Lattice.electron_id.is_(None))
            .order_by(Lattice.updated_at.desc())
        )

        run_time = await self.db_con.scalar(
            select(
                func.sum(
                    func.coalesce(
                        extract("epoch", Lattice.completed_at),
                        extract("epoch", func.now()),
                    )
                    - extract("epoch", Lattice.started_at)
                )
                * 1000
            ).filter(Lattice.is_active.is_not(False), Lattice.electron_id.is_(None))
        )

        total_jobs = await self.db_con.scalar(
            select(func.count(Lattice.id)).filter(
                Lattice.is_active.is_not(False), Lattice.electron_id.is_(None)
            )
        )
        total_failed = await self.get_dispatch_count_by_status(status="FAILED")
        total_jobs_cancelled = await self.get_dispatch_count_by_status(status="CANCELLED")
        total_jobs_new_object = await self.get_dispatch_count_by_status(status="NEW_OBJECT")

        run_time = 0 if run_time is None else run_time
        return DispatchDashBoardResponse(
            total_jobs_running=total_jobs_running,
            total_jobs_completed=total_jobs_done,
            latest_running_task_status=last_ran_job_status
            if last_ran_job_status is not None
            else None,
            total_dispatcher_duration=run_time if run_time is not None else 0,
            total_jobs_failed=total_failed,
            total_jobs_cancelled=total_jobs_cancelled,
            total_jobs_new_object=total_jobs_new_object,
            total_jobs=total_jobs,
        )

    async def delete_dispatches(self, data: DeleteDispatchesRequest) -> DeleteDispatchesResponse:
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
        if data.dispatches is None or len(data.dispatches) == 0:
            return DeleteDispatchesResponse(
                success_items=success,
                failure_items=failure,
                message=message,
            )
        for dispatch_id in data.dispatches:
            try:
                lattice_id = await self.db_con.scalar(
                    select(Lattice.id).where(
                        Lattice.dispatch_id == str(dispatch_id), Lattice.is_active.is_not(False)
                    )
                )
                if lattice_id is None:
                    failure.append(dispatch_id)
                    continue
                electron_ids = select(Electron.id).where(
                    Electron.parent_lattice_id == lattice_id,
                    Electron.is_active.is_not(False),
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
                await self.db_con.execute(
                    update_electron_dependency,
                    execution_options=immutabledict({"synchronize_session": False}),
                )
                update_electron = (
                    update(Electron)
                    .where(Electron.parent_lattice_id == lattice_id)
                    .values(
                        {
                            Electron.updated_at: datetime.now(timezone.utc),
                            Electron.is_active: False,
                        }
                    )
                )
                await self.db_con.execute(update_electron)

                update_lattice = (
                    update(Lattice)
                    .where(Lattice.id == lattice_id)
                    .values(
                        {
                            Lattice.updated_at: datetime.now(timezone.utc),
                            Lattice.is_active: False,
                        }
                    )
                )
                await self.db_con.execute(update_lattice)
                await self.db_con.commit()
                success.append(dispatch_id)
            except Exception:
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

    async def delete_all_dispatches(self, data: DeleteAllDispatchesRequest):
        """
        Delete dispatches
        Args:
            List[dispatch_id]
        Return:
            list of status(i.e whether given dispatch id is deleted successfully or failed)
        """
        success = []
        failure = []
        status_filters = await self.get_filters(data.status_filter)
        filter_dispatches = await self.db_con.execute(
            select(Lattice.id, Lattice.dispatch_id).where(
                or_(
                    Lattice.name.ilike(f"%{data.search_string}%"),
                    Lattice.dispatch_id.ilike(f"%{data.search_string}%"),
                ),
                Lattice.status.in_(status_filters),
                Lattice.is_active.is_not(False),
            )
        )
        dispatch_ids, dispatches = zip(
            *[(dispatch[0], uuid.UUID(dispatch[1])) for dispatch in filter_dispatches.all()]
        )
        if len(dispatches) >= 1:
            try:
                electron_ids = select(Electron.id).where(
                    Electron.parent_lattice_id.in_(dispatch_ids), Electron.is_active.is_not(False)
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
                await self.db_con.execute(
                    update_electron_dependency,
                    execution_options=immutabledict({"synchronize_session": False}),
                )
                await self.db_con.execute(
                    update_electron,
                    execution_options=immutabledict({"synchronize_session": False}),
                )
                await self.db_con.execute(
                    update_lattice,
                    execution_options=immutabledict({"synchronize_session": False}),
                )
                await self.db_con.commit()
                success = dispatches
            except Exception:
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

    async def get_filters(self, status_filter: Status):
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
