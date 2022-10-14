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

"""Model helper to handle sort by and sort direction"""

from enum import Enum


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
