import asyncio
import os

import nats
from dotenv import load_dotenv
from nats.errors import ConnectionClosedError, NoServersError, TimeoutError

load_dotenv()

TOPIC = os.environ.get("MQ_DISPATCH_TOPIC")
MQ_CONNECTION_URI = os.environ.get("MQ_CONNECTION_URI")

#
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     try:
#         asyncio.ensure_future(main)
