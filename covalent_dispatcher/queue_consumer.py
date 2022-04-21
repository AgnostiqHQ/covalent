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
import json
import os

import nats
import requests
from app.core.config import settings
from app.core.dispatcher_logger import logger
from app.core.get_svc_uri import DispatcherURI
from dotenv import load_dotenv

load_dotenv()

TOPIC = os.environ.get("MQ_DISPATCH_TOPIC")
MQ_CONNECTION_URI = os.environ.get("MQ_CONNECTION_URI")


def send_dispatch_id(dispatch_id: str):

    resp = requests.post(DispatcherURI().get_route(f"workflow/{dispatch_id}"))
    resp.raise_for_status()

    logger.warning(f"Dispatch id {dispatch_id} sent successfully.")


def get_status():
    resp = requests.get(DispatcherURI().get_route("workflow/status"))
    resp.raise_for_status()

    return resp.json()["status"]


async def main():
    """Pick up workflows from the message queue and dispatch them one by one."""
    nc = await nats.connect(MQ_CONNECTION_URI, connect_timeout=30)

    async def msg_handler(msg):
        dispatch_id = json.loads(msg.data.decode())["dispatch_id"]
        logger.warning(f"Got dispatch_id: {dispatch_id} with type {type(dispatch_id)}")
        while True:
            await asyncio.sleep(0.1)
            # logger.warning("Checking empty queue")
            if get_status() == "EMPTY":
                break

        send_dispatch_id(dispatch_id=dispatch_id)

    sub = await nc.subscribe(TOPIC, cb=msg_handler)

    print(f"Subscribed to topic: {TOPIC}")
    try:
        await sub.next_msg()
    except nats.errors.TimeoutError:
        pass


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.ensure_future(main())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
        pass
