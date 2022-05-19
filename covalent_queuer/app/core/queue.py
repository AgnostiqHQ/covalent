# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

"""Amazon Simple Queue Service (SQS) implementation of the workflow queue."""

import json
import logging
import os
from enum import Enum
from typing import Callable

import botocore.exceptions
from aiobotocore.session import ClientCreatorContext, get_session

MQ_QUEUE_MESSAGE_GROUP_ID = os.environ.get("MQ_QUEUE_MESSAGE_GROUP_ID")
MQ_QUEUE_REGION_NAME = os.environ.get("MQ_QUEUE_REGION_NAME")
MQ_QUEUE_MSG_WAIT_TIME = int(os.environ.get("MQ_QUEUE_MSG_WAIT_TIME"))

logger = logging.getLogger(__name__)


class AwsErrorCodes(Enum):
    NON_EXISTENT_QUEUE = "AWS.SimpleQueueService.NonExistentQueue"


class Queue:
    def __init__(
        self,
        queue_name: str = None,
        queue_url: str = None,
    ):
        self.queue_name = queue_name
        self.queue_url = queue_url

    def client_factory(self) -> ClientCreatorContext:
        """SQS client factory."""

        session = get_session()
        return session.create_client("sqs")

    async def get_queue_url(self) -> str:
        """Get the URL of the queue."""

        if self.queue_url:
            return self.queue_url

        async with self.client_factory() as client:
            try:
                response = await client.get_queue_url(QueueName=self.queue_name)
            except botocore.exceptions.ClientError as err:
                if err.response["Error"]["Code"] == AwsErrorCodes.NON_EXISTENT_QUEUE:
                    logging.error(f"Queue {self.queue_name} does not exist.")
                raise

            self.queue_url = response["QueueUrl"]
            return self.queue_url

    async def publish(
        self, message_body_dict: dict, message_group_id: str = MQ_QUEUE_MESSAGE_GROUP_ID
    ) -> dict:
        """Publish message to the queue.

        Args:
            message_body_dict: Message body takes the form {'dispatch_id': 'alpha_numeric_dispatch_id'}.
            message_group_id: Defaults to MQ_QUEUE_MESSAGE_GROUP_ID.

        Returns:
            Response from client when message is published.
        """

        async with self.client_factory() as client:
            queue_url = await self.get_queue_url()
            message_body_str = json.dumps(message_body_dict)
            response = await client.send_message(
                QueueUrl=queue_url,
                MessageBody=message_body_str,
                MessageGroupId=message_group_id,
            )
            return response

    async def poll_queue(self, message_handler: Callable) -> None:
        """Poll for messages published to the queue and apply the message handler.

        Args:
            message_handler:
                Function to apply to the message. The function takes a single input of a message body in json format.
        """

        async with self.client_factory() as client:
            queue_url = await self.get_queue_url()

            while True:
                response = await client.receive_message(
                    QueueUrl=queue_url, WaitTimeSeconds=MQ_QUEUE_MSG_WAIT_TIME
                )
                if "Messages" in response:
                    for msg in response["Messages"]:
                        msg_body = json.loads(msg["Body"])
                        try:
                            await message_handler(msg_body)
                            await client.delete_message(
                                QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"]
                            )
                        except Exception as err:
                            logging.error(err)
                            logging.exception(
                                f"Message {msg['ReceiptHandle']} was not able to be processed."
                            )
