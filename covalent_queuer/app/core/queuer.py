import json
import logging
from enum import Enum
from typing import Any

import nats
from app.core.config import settings
from covalent._shared_files.util_classes import Timer


class QueueTopics(Enum):
    DISPATCH = settings.MQ_DISPATCH_TOPIC


class Queuer:
    topics: QueueTopics = QueueTopics
    timer = Timer()

    def get_client(self) -> Any:
        print(
            self.timer.start(endpoint='queuer_get_client', descriptor=f"The connection to {settings.MQ_CONNECTION_URI}",
                             service=self.timer.QUEUER,
                             dispatch_id=settings.MQ_DISPATCH_TOPIC,
                             )
        )
        print(self.timer.stop(endpoint='queuer_get_client',
                              descriptor=f"Connection to {settings.MQ_CONNECTION_URI}",
                              service=self.timer.QUEUER,
                              dispatch_id=settings.MQ_DISPATCH_TOPIC,
                              )
              )
        return nats.connect(settings.MQ_CONNECTION_URI)

    async def publish(self, topic: str, msg: Any) -> Any:
        # get enum value
        print(self.timer.start(endpoint="queuer_publish",
                               descriptor=f"Publishing message to topic {topic}",
                               service=self.timer.QUEUER,
                               dispatch_id=settings.MQ_DISPATCH_TOPIC
                               )
              )
        topic = topic.value
        client = await self.get_client()
        msg_json = json.dumps(msg)
        logging.info(f"Publishing message to topic {topic}:")
        logging.info(msg_json)
        res = await client.publish(topic, msg_json.encode())
        print(self.timer.stop(endpoint="queuer_publish",
                              descriptor="Publish message action",
                              service=self.timer.QUEUER,
                              dispatch_id=settings.MQ_DISPATCH_TOPIC
                              )
              )
        return res
