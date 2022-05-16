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

import botocore.exceptions
from aiobotocore.session import get_session
from app.core.config import settings

MQ_QUEUE_MESSAGE_GROUP_ID = os.environ.get("MQ_QUEUE_MESSAGE_GROUP_ID")
MQ_QUEUE_REGION_NAME = os.environ.get("MQ_QUEUE_REGION_NAME")

logger = logging.getLogger(__name__)


class AwsErrorCodes(Enum):
    NON_EXISTENT_QUEUE = "AWS.SimpleQueueService.NonExistentQueue"


class Queue:
    def __init__(self, queue_name: str = None, queue_url: str = None):
        self.queue_name = queue_name
        self.queue_url = queue_url

    def client_factory(self):
        session = get_session()
        return session.create_client("sqs", region_name=MQ_QUEUE_REGION_NAME)

    async def get_queue_url(self):
        if self.queue_url:
            return self.queue_url

        async with self.client_factory() as client:
            # TODO - clarify why there was a queue_name = self.queue_name before
            try:
                response = await client.get_queue_url(QueueName=self.queue_name)
            except botocore.exceptions.ClientError as err:
                if err.response["Error"]["Code"] == AwsErrorCodes.NON_EXISTENT_QUEUE:
                    logging.error(f"Queue {self.queue_name} does not exist.")
                else:
                    raise

            queue_url = response["QueueUrl"]
            self.queue_url = queue_url
            return queue_url

    async def publish(self, message_body_dict):
        async with self.client_factory() as client:
            queue_url = await self.get_queue_url()
            message_body_str = json.dumps(message_body_dict)
            response = await client.send_message(
                QueueUrl=queue_url,
                DelaySeconds=10,
                MessageBody=message_body_str,
                MessageGroupId=MQ_QUEUE_MESSAGE_GROUP_ID,
            )
            return response

    async def poll_queue(self, message_handler):
        async with self.client_factory() as client:
            queue_name = self.queue_name
            queue_url = await self.get_queue_url()
            while True:
                try:
                    response = await client.receive_message(
                        QueueUrl=queue_url,
                        WaitTimeSeconds=1,
                        MaxNumberOfMessages=10,
                    )

                    if "Messages" in response:
                        for msg in response["Messages"]:
                            try:
                                await message_handler(client, msg)
                                await client.delete_message(
                                    QueueUrl=self.queue_url, ReceiptHandle=msg["ReceiptHandle"]
                                )
                            except Exception as err:
                                logging.error(err)
                                logging.exception(
                                    f"Message {msg['ReceiptHandle']} was not able to be processed."
                                )

                except KeyboardInterrupt:
                    break
            logging.info(f"Shutting down message handlers for queue {queue_name}")
            await client.close()


class DispatchQueue(Queue):
    def __init__(self):
        super().__init__(settings.DISPATCH_QUEUE)

    async def run(self):
        logging.info(f"Registering polling message handler for queue {self.queue_name}...")
        await self.poll_queue(self.message_handler)
        return self

    async def message_handler(self, client, msg):
        logging.info(f'Got msg: {msg["Body"]}')


class UpdateWorkflowQueue(Queue):
    def __init__(self):
        super().__init__(settings.DISPATCH_QUEUE)

    async def run(self):
        logging.info(f"Registering polling message handler for queue {self.queue_name}...")
        await self.poll_queue(self.message_handler)
        return self

    async def message_handler(self, client, msg):
        logging.info(f'Got msg: {msg["Body"]}')


class CreateScheduleQueue(Queue):
    def __init__(self):
        super().__init__(settings.WORKFLOW_CREATE_SCHEDULE_QUEUE)

    async def run(self):
        logging.info(f"Registering polling message handler for queue {self.queue_name}...")
        await self.poll_queue(self.message_handler)
        return self

    async def message_handler(self, client, msg):
        logging.info(f'Got msg: {msg["Body"]}')
