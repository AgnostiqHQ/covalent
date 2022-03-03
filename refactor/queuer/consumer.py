import asyncio

import nats
from nats.errors import ConnectionClosedError, NoServersError, TimeoutError

TOPIC = "foo"
MQ_CONNECTION_URI = "localhost:4222"


async def main():
    print("Connecting to NATS...")
    nc = await nats.connect(MQ_CONNECTION_URI)

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print(
            "Received a message on '{subject} {reply}': {data}".format(
                subject=subject, reply=reply, data=data
            )
        )

    print(f"Subscribing to topic: {TOPIC}\nListening for messages...")
    sub = await nc.subscribe(TOPIC, cb=message_handler)

    try:
        async for msg in sub.messages:
            print(f"Received a message on '{msg.subject} {msg.reply}': {msg.data.decode()}")
            await sub.unsubscribe()
    except Exception as e:
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
