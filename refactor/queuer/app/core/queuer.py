from enum import Enum
import json
import os

import nats
from typing import Any

from refactor.queuer.app.core.config import settings

class QueueTopics(Enum):
    DIPATCH = settings.MQ_DISPATCH_TOPIC

class Queuer():

    topics: QueueTopics = QueueTopics

    def get_client(self) -> Any:
       return nats.connect(settings.MQ_CONNECTION_URI)

    async def publish(self, topic: str, msg: Any) -> Any:
        client = await self.get_client()
        res = await client.publish(topic, json.dumps(msg).encode())
        return res
