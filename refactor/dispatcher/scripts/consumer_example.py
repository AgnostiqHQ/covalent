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
import time

import nats
from dotenv import load_dotenv
from nats.errors import ConnectionClosedError, NoServersError, TimeoutError

load_dotenv()

TOPIC = os.environ.get("MQ_DISPATCH_TOPIC")
MQ_CONNECTION_URI = os.environ.get("MQ_CONNECTION_URI")


def complete_workflow():
    time.sleep(10)
    return True


async def main():
    print("Connecting to NATS...")
    nc = await nats.connect(MQ_CONNECTION_URI)

    async def msg_handler(msg):
        data = msg.data.decode()
        print(f"Workflow dispatched with id: {data}")
        print("starting workflow ...")
        complete_workflow()
        print("workflow done")

    # TODO - We need to pick up the dispatch id and submit the corresponding workflow
    print(f"Subscribing to topic {TOPIC}.\nListening for msgs ... ")
    sub = await nc.subscribe(TOPIC, cb=msg_handler)

    # try:
    #     async for msg in sub.messages:
    #         print(f"Received a message on '{msg.subject} {msg.reply}': {msg.data.decode()}")
    #         await sub.unsubscribe()
    # except Exception as e:
    #     pass

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
