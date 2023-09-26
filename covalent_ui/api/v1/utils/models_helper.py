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

"""Model helper to handle sort by and sort direction"""

from enum import Enum


class CaseInsensitiveEnum(Enum):
    """Enum overriden to support case insensitive keys"""

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value.upper() == value.upper():
                return member


class SortBy(CaseInsensitiveEnum):
    """Values to filter data by"""

    RUNTIME = "runtime"
    STATUS = "status"
    STARTED = "started_at"
    LATTICE_NAME = "lattice_name"
    ENDED = "ended_at"


class JobsSortBy(CaseInsensitiveEnum):
    """Values to filter jobs data by"""

    EXECUTOR = "executor"
    JOB_ID = "job_id"
    START_TIME = "start_time"
    STATUS = "status"


class SortDirection(CaseInsensitiveEnum):
    """Values to decide sort direction"""

    ASCENDING = "ASC"
    DESCENDING = "DESC"
