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
import logging
import os

import requests
from app.core.dispatcher_logger import logger
from app.core.get_svc_uri import DispatcherURI
from app.core.queue import Queue
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

MQ_QUEUE_NAME = os.environ.get("MQ_QUEUE_NAME")


def send_dispatch_id(dispatch_id: str) -> None:
    """Submit workflow by sending dispatch id to Dispatcher service.

    Args:
        dispatch_id: identifier of the workflow to be submitted.
    """

    resp = requests.post(DispatcherURI().get_route(f"workflow/{dispatch_id}"))
    resp.raise_for_status()

    logger.warning(f"Dispatch id {dispatch_id} sent successfully.")


async def main():
    """Pick up workflows from the message queue and dispatch them one by one."""

    queue = Queue(queue_name=MQ_QUEUE_NAME)

    async def msg_handler(msg: dict) -> None:
        dispatch_id = msg["dispatch_id"]
        logger.info(f"Got dispatch_id: {dispatch_id} with type {type(dispatch_id)}")
        send_dispatch_id(dispatch_id=dispatch_id)

    try:
        await queue.poll_queue(message_handler=msg_handler)
    except Exception as err:
        logging.error(f"Queue consumer could not poll queue for messages: {err}.")
        raise


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.ensure_future(main())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
