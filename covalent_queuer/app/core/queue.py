import json
import logging
from enum import Enum
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

QUEUE_NAME = "workflow_queue.fifo"
logger = logging.getLogger(__name__)


class Queue:
    def get_queue(self) -> Any:
        """Get AWS Simple Queue Service queue."""

        sqs_resource = boto3.resource("sqs")
        try:
            queue = sqs_resource.get_queue_by_name(QueueName=QUEUE_NAME)
        except Exception:
            logger.exception("Queue not found.")
        return queue

    async def send_message(self, message_body: str):
        """Send message to an AWS SQS queue.

        message_body: The body of the messsage, in this case a dispatch id for a workflow.
        """

        queue = self.get_queue()
        try:
            response = queue.send_message(MessageBody=message_body)
        except ClientError as error:
            logger.exception(f"Send message failed: {message_body}")
            raise error
        else:
            return response
