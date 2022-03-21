# TODO - How do I publish a message that the subscriber can see?

import asyncio
import os

import nats
from dotenv import load_dotenv

load_dotenv()

TOPIC = os.environ.get("MQ_DISPATCH_TOPIC")
MQ_CONNECTION_URI = os.environ.get("MQ_CONNECTION_URI")


# TODO - Is there a strong reason for using asyncio in this case?


async def main():
    nc = await nats.connect(MQ_CONNECTION_URI)
    await nc.publish(TOPIC, b"lkjlkjsgdfsg4df65g46")


if __name__ == "__main__":
    asyncio.run(main())
