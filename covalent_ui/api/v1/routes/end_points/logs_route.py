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
