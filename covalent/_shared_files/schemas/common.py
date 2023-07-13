# Copyright 2023 Agnostiq Inc.
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

"""FastAPI models for /api/v1/resultv2 endpoints"""

from enum import Enum

from covalent._shared_files.util_classes import RESULT_STATUS


class StatusEnum(str, Enum):
    NEW_OBJECT = str(RESULT_STATUS.NEW_OBJECT)
    STARTING = str(RESULT_STATUS.STARTING)
    PENDING_REUSE = str(RESULT_STATUS.PENDING_REUSE)
    PENDING_REPLACEMENT = str(RESULT_STATUS.PENDING_REPLACEMENT)
    COMPLETED = str(RESULT_STATUS.COMPLETED)
    POSTPROCESSING = str(RESULT_STATUS.POSTPROCESSING)
    FAILED = str(RESULT_STATUS.FAILED)
    RUNNING = str(RESULT_STATUS.RUNNING)
    CANCELLED = str(RESULT_STATUS.CANCELLED)
    DISPATCHING = str(RESULT_STATUS.DISPATCHING)
