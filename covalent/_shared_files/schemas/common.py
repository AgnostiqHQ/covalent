# Copyright 2023 Agnostiq Inc.
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

"""FastAPI models for /api/v1/resultv2 endpoints"""

from enum import Enum

from covalent._shared_files.util_classes import RESULT_STATUS


class StatusEnum(str, Enum):
    NEW_OBJECT = str(RESULT_STATUS.NEW_OBJECT)
    STARTING = str(RESULT_STATUS.STARTING)
    PENDING_REUSE = str(RESULT_STATUS.PENDING_REUSE)  # For redispatch in the new dispatcher design
    PENDING_REPLACEMENT = str(
        RESULT_STATUS.PENDING_REPLACEMENT
    )  # For redispatch in the new dispatcher design
    COMPLETED = str(RESULT_STATUS.COMPLETED)
    POSTPROCESSING = str(RESULT_STATUS.POSTPROCESSING)
    FAILED = str(RESULT_STATUS.FAILED)
    RUNNING = str(RESULT_STATUS.RUNNING)
    CANCELLED = str(RESULT_STATUS.CANCELLED)
    DISPATCHING = str(RESULT_STATUS.DISPATCHING)
