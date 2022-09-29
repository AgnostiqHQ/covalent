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


import asyncio
from typing import Any, NamedTuple

from . import logger

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class SafeVariable(asyncio.Queue):
    def __init__(self, event_loop=None) -> None:
        self.event_loop = event_loop or asyncio.get_event_loop()
        super().__init__(maxsize=1)

    def put_nowait_safe(self, value: Any) -> None:
        self.event_loop.call_soon_threadsafe(self.put_nowait, value)

    def get_nowait_safe(self) -> Any:
        return self.event_loop.call_soon_threadsafe(self.get_nowait, ())

    def save(self, value: Any) -> None:
        try:
            self.put_nowait_safe(value)
        except asyncio.QueueFull:
            self.get_nowait_safe()
            self.put_nowait_safe(value)

    def retrieve(self) -> Any:
        try:
            value = self.get_nowait_safe()
            self.put_nowait_safe(value)
            return value
        except asyncio.QueueEmpty:
            return None

    async def retrieve_async(self) -> Any:
        return await self.get()


# TODO: Following definitions are for legacy reasons only and should be removed soon:
# {


class Status:
    def __init__(self, STATUS) -> None:
        self.STATUS = STATUS

    def __str__(self) -> str:
        return self.STATUS


class DispatchInfo(NamedTuple):
    """
    Information about a dispatch to be shared to a task post dispatch.

    Attributes:
        dispatch_id: Dispatch id of the dispatch.
    """

    dispatch_id: str


# }
