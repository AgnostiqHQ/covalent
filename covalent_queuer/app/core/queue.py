import json
import logging
from enum import Enum
from typing import Any

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class Queue:
    def get_queue(self) -> Any:
        """Get AWS Simple Queue Service queue."""

        sqs_resource = boto3.resource("sqs")
        try:
            queue = sqs_resource.get_queue_by_name(QueueName="workflow_queue.fifo")
        except Exception:
            logger.exception("Queue not found.")
        return queue

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
