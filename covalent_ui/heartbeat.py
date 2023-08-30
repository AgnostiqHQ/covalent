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
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List

import aiofiles
from fastapi import FastAPI

from covalent._shared_files.config import get_config
from covalent_ui.api.v1.routes.end_points.summary_routes import get_all_dispatches
from covalent_ui.api.v1.utils.status import Status


class Heartbeat:
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f%z"

    def __init__(
        self,
        beat_interval: int = None,
        beat_file: str = None,
    ):
        self.beat_interval = beat_interval or get_config("dispatcher.heartbeat_interval")
        self.beat_file = beat_file or get_config("dispatcher.heartbeat_file")

    async def start(self):
        while True:
            await self.beat()
            await asyncio.sleep(self.beat_interval)

    async def beat(self):
        async with aiofiles.open(self.beat_file, mode="w") as file:
            await file.write(
                f"ALIVE {datetime.now(tz=timezone.utc).strftime(Heartbeat.TIMESTAMP_FORMAT)}"
            )

    @staticmethod
    def stop():
        with open(get_config("dispatcher.heartbeat_file"), mode="w") as file:
            file.write(
                f"DEAD {datetime.now(tz=timezone.utc).strftime(Heartbeat.TIMESTAMP_FORMAT)}"
            )


async def cancel_all_with_status(status: Status) -> List[str]:
    from covalent_dispatcher._core.dispatcher import cancel_dispatch

    dispatch_ids = []
    page = 0
    count = 100

    while True:
        dispatches = get_all_dispatches(
            count=count,
            offset=page * count,
            status_filter=status,
        )

        dispatch_ids += [dispatch.dispatch_id for dispatch in dispatches.items]

        if dispatches.total_count == page * count + len(dispatches.items):
            break

        page += 1

    for dispatch_id in dispatch_ids:
        await cancel_dispatch(dispatch_id)

    return dispatch_ids


@asynccontextmanager
async def lifespan(app: FastAPI):
    heartbeat = Heartbeat()
    asyncio.create_task(heartbeat.start())

    yield

    for status in [
        Status.NEW_OBJECT,
        Status.POSTPROCESSING,
        Status.PENDING_POSTPROCESSING,
        Status.RUNNING,
    ]:
        await cancel_all_with_status(status)

    Heartbeat.stop()
