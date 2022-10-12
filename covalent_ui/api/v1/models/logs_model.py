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

"""Logs response model"""


from typing import List, Optional, Union

from pydantic import BaseModel, conint

from covalent_ui.api.v1.utils.models_helper import CaseInsensitiveEnum, SortDirection


class SortBy(CaseInsensitiveEnum):
    """Values to filter data by"""

    LOG_DATE = "log_date"
    STATUS = "status"


class LogsRequest(BaseModel):
    """Logs request model"""

    count: conint(gt=0, lt=100)
    offset: Optional[conint(gt=-1)] = 0
    sort_by: Optional[SortBy] = SortBy.LOG_DATE
    search: Optional[str] = ""
    direction: Optional[SortDirection] = SortDirection.DESCENDING


class LogsModule(BaseModel):
    """Dispatch Modeule Validation"""

    log_date: Union[str, None] = None
    status: str = "INFO"
    message: Optional[Union[str, None]]


class LogsResponse(BaseModel):
    """Dispatch Response Model"""

    items: List[LogsModule]
    total_count: Union[int, None] = None

    class Config:
        """Configure example for openAPI"""

        schema_extra = {
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
