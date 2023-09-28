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


from dataclasses import dataclass
from typing import NamedTuple


@dataclass
class Status:
    STATUS: str

    def __bool__(self):
        """
        Return True if the status is not "NEW_OBJECT"
        """

        return self.STATUS != "NEW_OBJECT"

    def __str__(self) -> str:
        return self.STATUS

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, self.__class__):
            return self.STATUS == __value.STATUS
        elif isinstance(__value, str):
            return self.STATUS == __value
        return False

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)


class RESULT_STATUS:
    NEW_OBJECT = Status("NEW_OBJECT")
    STARTING = Status("STARTING")  # Dispatch level
    PENDING_REUSE = Status("PENDING_REUSE")  # For redispatch
    COMPLETED = Status("COMPLETED")
    POSTPROCESSING = Status("POSTPROCESSING")
    PENDING_POSTPROCESSING = Status("PENDING_POSTPROCESSING")
    POSTPROCESSING_FAILED = Status("POSTPROCESSING_FAILED")
    FAILED = Status("FAILED")
    RUNNING = Status("RUNNING")
    CANCELLED = Status("CANCELLED")
    DISPATCHING_SUBLATTICE = Status("DISPATCHING_SUBLATTICE")  # Sublattice dispatch status


class DispatchInfo(NamedTuple):
    """
    Information about a dispatch to be shared to a task post dispatch.

    Attributes:
        dispatch_id: Dispatch id of the dispatch.
    """

    dispatch_id: str
