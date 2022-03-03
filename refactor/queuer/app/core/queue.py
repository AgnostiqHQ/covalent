import json
from typing import Any
import nats

MQ_CONNECTION_URI = "localhost:4222"

class Queuer():
    def get_client(self) -> Any:
       return nats.connect(MQ_CONNECTION_URI)

    async def publish(self, topic: str, msg: Any) -> Any:
        client = await self.get_client()
        res = await client.publish(topic, json.dumps(msg).encode())
        return res


