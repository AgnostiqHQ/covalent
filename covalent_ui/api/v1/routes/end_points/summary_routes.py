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

"""Summary Routes"""

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import Field
from sqlalchemy.orm import Session
from typing_extensions import Annotated

import covalent_ui.api.v1.database.config.db as db
from covalent_ui.api.v1.data_layer.summary_dal import Summary
from covalent_ui.api.v1.models.dispatch_model import (
    DeleteAllDispatchesRequest,
    DeleteDispatchesRequest,
    DeleteDispatchesResponse,
    DispatchDashBoardResponse,
    SortBy,
    SortDirection,
)
from covalent_ui.api.v1.utils.status import Status

routes: APIRouter = APIRouter()


@routes.get("/list")
def get_all_dispatches(
    count: Optional[Annotated[int, Field(gt=0, lt=100)]] = Query(10),
    offset: Optional[Annotated[int, Field(gt=-1)]] = 0,
    sort_by: Optional[SortBy] = SortBy.RUNTIME,
    search: Optional[str] = "",
    sort_direction: Optional[SortDirection] = SortDirection.DESCENDING,
    status_filter: Optional[Status] = Status.ALL,
):
    """Get All Dispatches

    Args:
        req: Dispatch Summary Request

    Returns:
        List of Dispatch Summary
    """
    with Session(db.engine) as session:
        summary = Summary(session)
        return summary.get_summary(count, offset, sort_by, search, sort_direction, status_filter)


@routes.get("/overview", response_model=DispatchDashBoardResponse)
def get_dashboard_details():
    """Overview of Dispatches

    Args:
        None

    Returns:
        An Overview of dispatches as object
    """
    with Session(db.engine) as session:
        summary = Summary(session)
        return summary.get_summary_overview()


@routes.post("/delete", response_model=DeleteDispatchesResponse)
def delete_dispatches(req: Optional[DeleteDispatchesRequest]):
    """Delete one or more Dispatches

    Args:
        req: Dispatch Dispatch Request

    Returns:
        List of deleted dispatches if success
        List of deleted dispatches if fails
    """

    with Session(db.engine) as session:
        summary = Summary(session)
        return summary.delete_dispatches(req)


@routes.post("/delete-all", response_model=DeleteDispatchesResponse)
def delete_all_dispatches(req: Optional[DeleteAllDispatchesRequest]):
    """Delete one or more Dispatches

    Args:
        req: Dispatch Dispatch Request

    Returns:
        List of deleted dispatches if success
        List of deleted dispatches if fails
    """

    with Session(db.engine) as session:
        summary = Summary(session)
        return summary.delete_all_dispatches(req)
