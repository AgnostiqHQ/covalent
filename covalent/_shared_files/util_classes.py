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
import queue
from multiprocessing.queues import Queue as MPQ
from typing import Any, NamedTuple

from . import logger

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class SafeVariable(MPQ):
    def __init__(self) -> None:
        super().__init__(maxsize=1, ctx=mp.get_context())

    def save(self, value: Any) -> None:
        try:
            self.put(value, timeout=0.5)
        except queue.Full:
            self.get_nowait()
            self.put_nowait(value)

    def retrieve(self) -> Any:
        try:
            value = self.get(timeout=0.5)
            self.put(value, timeout=0.5)
            return value
        except queue.Empty:
            return None


class DispatchInfo(NamedTuple):
    """
    Information about a dispatch to be shared to a task post dispatch.

    Attributes:
        dispatch_id: Dispatch id of the dispatch.
    """

    dispatch_id: str
