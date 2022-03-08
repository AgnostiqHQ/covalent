import json
import os

import nats
from typing import Any

class Queuer():

    def get_client(self) -> Any:
       MQ_CONNECTION_URI = os.environ.get("MQ_CONNECTION_URI")
       return nats.connect(MQ_CONNECTION_URI)

    async def publish(self, topic: str, msg: Any) -> Any:
        client = await self.get_client()
        res = await client.publish(topic, json.dumps(msg).encode())
        return res
