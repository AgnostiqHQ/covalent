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
# Relief from the License may be granted by purchasing a commercial license.

"""Dispatch request and response model"""


from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, conint

from covalent_ui.api.v1.utils.status import Status


class CaseInsensitiveEnum(Enum):
    """Enum overriden to support case insensitive keys"""

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value == value.upper():
                return member


class SortBy(CaseInsensitiveEnum):
    """Values to filter data by"""

    RUNTIME = "runtime"
    STATUS = "status"
    STARTED = "started_at"
    LATTICE_NAME = "lattice_name"
    ENDED = "ended_at"


class SortDirection(CaseInsensitiveEnum):
    """Values to decide sort direction"""

    ASCENDING = "ASC"
    DESCENDING = "DESC"


class DispatchSummaryRequest(BaseModel):
    count: conint(gt=0, lt=100)
    offset: Optional[conint(gt=-1)] = 0
    sort_by: Optional[SortBy] = SortBy.STARTED
    search: Optional[str] = ""
    direction: Optional[SortDirection] = SortDirection.DESCENDING


class DispatchModule(BaseModel):
    """Dispatch Modeule Validation"""

    dispatch_id: str
    lattice_name: str
    runtime: Optional[Union[int, None]]
    total_electrons: Optional[Union[int, None]]
    total_electrons_completed: Optional[Union[int, None]]
    started_at: Optional[Union[datetime, None]]
    ended_at: Optional[Union[datetime, None]]
    status: Status
    updated_at: Optional[Union[datetime, None]]


class DispatchResponse(BaseModel):
    """Dispatch Response Model"""

    items: List[DispatchModule]
    total_count: int

    class Config:
        """Configure example for openAPI"""

        schema_extra = {
            "example": {
                "dispatches": [
                    {
                        "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac16",
                        "lattice_name": "testing content",
                        "runtime": 1,
                        "started_time": "2022-06-13T07:45:02.114328+00:00",
                        "end_time": "2022-06-13T07:45:02.216474+00:00",
                        "status": "COMPLETED",
                    }
                ],
                "total_count": 10,
            }
        }


class DeleteDispatchesRequest(BaseModel):
    """Dashboard metadate model"""

    dispatches: List[UUID]


class DeleteDispatchesResponse(BaseModel):
    """Dashboard metadate model"""

    success_items: List[UUID]
    failure_items: List[UUID] = None
    message: str = None


class DispatchDashBoardResponse(BaseModel):
    """Dashboard metadate model"""

    total_jobs: int = None
    total_jobs_running: int = None
    total_jobs_completed: int = None
    total_jobs_failed: int = None
    latest_running_task_status: Status = None
    total_dispatcher_duration: int = None

    class Config:
        """Configure example for openAPI"""

        schema_extra = {
            "example": {
                "total_jobs_running": 5,
                "total_jobs_done": 20,
                "latest_running_task_status": "COMPLETED",
                "total_dispatcher_duration": 90,
            }
        }
