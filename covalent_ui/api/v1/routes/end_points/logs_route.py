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

"""Logs Routes"""

from typing import Optional

from fastapi import APIRouter, Query

from covalent_ui.api.v1.data_layer.logs_dal import Logs
from covalent_ui.api.v1.models.logs_model import SortBy, SortDirection

routes: APIRouter = APIRouter()


@routes.get("/")
def get_logs(
    count: Optional[int] = Query(0),
    offset: Optional[int] = Query(0),
    sort_by: Optional[SortBy] = SortBy.LOG_DATE,
    search: Optional[str] = "",
    sort_direction: Optional[SortDirection] = SortDirection.DESCENDING,
):
    logs = Logs()
    return logs.get_logs(sort_by, sort_direction, search, count, offset)


@routes.get("/download")
def download_logs():
    logs = Logs()
    return logs.download_logs()
