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

"""Summary Routes"""

from fastapi import APIRouter
from sqlalchemy.orm import Session

from covalent_ui.app.api_v0.data_layer.summary_dal import Summary
from covalent_ui.app.api_v0.database.config.db import engine
from covalent_ui.app.api_v0.models.dispatch_model import (
    DeleteDispatchesRequest,
    DeleteDispatchesResponse,
    DispatchDashBoardResponse,
    DispatchSummaryRequest,
)

routes: APIRouter = APIRouter()


@routes.post("/")
def get_all_dispatches(req: DispatchSummaryRequest):
    """Get All Dispatches

    Args:
        req: Dispatch Summary Request

    Returns:
        List of Dispatch Summary
    """
    with Session(engine) as session:
        summary = Summary(session)
        return summary.get_summary(req)


@routes.get("/overview/", response_model=DispatchDashBoardResponse)
def get_dashboard_details():
    """Overview of Dispatches

    Args:
        None

    Returns:
        An Overview of dispatches as object
    """
    with Session(engine) as session:
        summary = Summary(session)
        return summary.get_summary_overview()


@routes.post("/delete", response_model=DeleteDispatchesResponse)
def delete_dispatches(req: DeleteDispatchesRequest):
    """Delete one or more Dispatches

    Args:
        req: Dispatch Dispatch Request

    Returns:
        List of deleted dispatches if success
        List of deleted dispatches if fails
    """

    with Session(engine) as session:
        summary = Summary(session)
        return summary.delete_dispatches(req)
