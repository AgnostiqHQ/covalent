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

"""Logs response model"""


from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated

from covalent_ui.api.v1.utils.models_helper import CaseInsensitiveEnum, SortDirection


class SortBy(CaseInsensitiveEnum):
    """Values to filter data by"""

    LOG_DATE = "log_date"
    STATUS = "status"


class LogsRequest(BaseModel):
    """Logs request model"""

    count: Annotated[int, Field(gt=0, lt=100)]
    offset: Optional[Annotated[int, Field(gt=-1)]] = 0
    sort_by: Optional[SortBy] = SortBy.LOG_DATE
    search: Optional[str] = ""
    direction: Optional[SortDirection] = SortDirection.DESCENDING


class LogsModule(BaseModel):
    """Dispatch Modeule Validation"""

    log_date: Union[str, None] = None
    status: str = "INFO"
    message: Optional[Union[str, None]] = None


class LogsResponse(BaseModel):
    """Dispatch Response Model"""

    items: List[LogsModule]
    total_count: Union[int, None] = None
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "log_date": "2022-06-13T07:45:02.114328+00:00",
                        "status": "INFO",
                        "message": "Application Started",
                    }
                ],
                "total_count": 1,
            }
        }
    )
