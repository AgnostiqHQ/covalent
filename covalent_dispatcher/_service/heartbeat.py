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

import asyncio
from datetime import datetime, timezone

import aiofiles

from covalent._shared_files.config import get_config


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
