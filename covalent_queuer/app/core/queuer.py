import json
import logging
from enum import Enum
from typing import Any

import boto3
import nats
from app.core.config import settings
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
sqs = boto3.resource("sqs")


class QueueTopics(Enum):
    DISPATCH = settings.MQ_DISPATCH_TOPIC


class Queue:

    topics: QueueTopics = QueueTopics

    def get_client(self) -> Any:
        return nats.connect(settings.MQ_CONNECTION_URI)

    async def send_message(self, queue, message_body, message_attributes=None):
        """
        Send a message to an Amazon SQS queue.

        :param queue: The queue that receives the message.
        :param message_body: The body text of the message.
        :param message_attributes: Custom attributes of the message. These are key-value
                                pairs that can be whatever you want.
        :return: The response from SQS that contains the assigned message ID.
        """
        if not message_attributes:
            message_attributes = {}

        try:
            response = queue.send_message(
                MessageBody=message_body, MessageAttributes=message_attributes
            )
        except ClientError as error:
            logger.exception("Send message failed: %s", message_body)
            raise error
        else:
            return response

    async def publish(self, topic: str, msg: Any) -> Any:
        # get enum value
        topic = topic.value
        client = await self.get_client()
        msg_json = json.dumps(msg)
        logging.info(f"Publishing message to topic {topic}:")
        logging.info(msg_json)
        res = await client.publish(topic, msg_json.encode())
        return res

    # TODO - Are topics necessary? How to add topics to SQS

    # TODO - Add method to connect to Amazon SQS

    # TODO - Add method to publish to SQS
