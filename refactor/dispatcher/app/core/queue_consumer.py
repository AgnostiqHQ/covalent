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
import os
from multiprocessing import Queue as MPQ

import nats
from app.core.queue_consumer import submit_workflow
from dotenv import load_dotenv

load_dotenv()

BASE_URI = os.environ.get("DATA_OS_SVC_HOST_URI")
TOPIC = os.environ.get("MQ_DISPATCH_TOPIC")
MQ_CONNECTION_URI = os.environ.get("MQ_CONNECTION_URI")

workflow_status_queue = MPQ()


async def main():
    """Pick up workflows from the message queue and dispatch them one by one."""

    nc = await nats.connect(MQ_CONNECTION_URI)

    async def msg_handler(msg):
        dispatch_id = msg.data.decode()

        while True:
            await asyncio.sleep(0.5)
            if workflow_status_queue.empty():
                break

        submit_workflow(dispatch_id)

    sub = await nc.subscribe(TOPIC, cb=msg_handler)

    try:
        await sub.next_msg()
    except:
        pass


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(main())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
