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


import multiprocessing as mp
from dataclasses import dataclass
from multiprocessing.queues import Queue as MPQ
from typing import Any, NamedTuple


class StatusStore(MPQ):
    def __init__(self, maxsize: int = 1) -> None:
        ctx = mp.get_context()
        super().__init__(maxsize, ctx=ctx)

    def save(self, value: Any) -> None:
        print("Saving things")
        self.put_nowait(value)

    def retrieve(self) -> Any:
        print("Retrieving things")
        return self.get_nowait()


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


class RESULT_STATUS:
    NEW_OBJECT = Status("NEW_OBJECT")
    COMPLETED = Status("COMPLETED")
    POSTPROCESSING = Status("POSTPROCESSING")
    PENDING_POSTPROCESSING = Status("PENDING_POSTPROCESSING")
    POSTPROCESSING_FAILED = Status("POSTPROCESSING_FAILED")
    FAILED = Status("FAILED")
    RUNNING = Status("RUNNING")
    CANCELLED = Status("CANCELLED")


class DispatchInfo(NamedTuple):
    """
    Information about a dispatch to be shared to a task post dispatch.

    Attributes:
        dispatch_id: Dispatch id of the dispatch.
    """

    dispatch_id: str
