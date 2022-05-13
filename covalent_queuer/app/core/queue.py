import json
import logging
import os
from enum import Enum
from typing import Any

import boto3
import botocore.exceptions
from aiobotocore.session import get_session
from app.core.config import settings
from botocore.exceptions import ClientError

MQ_QUEUE_NAME = os.environ.get("MQ_QUEUE_NAME")
logger = logging.getLogger(__name__)


class Queue:
    def get_queue(self) -> Any:
        """Get AWS Simple Queue Service queue."""

        sqs_resource = boto3.resource("sqs")
        try:
            queue = sqs_resource.get_queue_by_name(QueueName=MQ_QUEUE_NAME)

        # TODO - Figure our proper way to catch Queue Not Found exception
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

            # TODO - Figure out how to do logging properly
            logger.exception(f"Send message failed: {message_body}")
            raise error
        else:
            return response


class AwsErrorCodes(Enum):
    NON_EXISTENT_QUEUE = "AWS.SimpleQueueService.NonExistentQueue"


class Queuer:

    queue_name = None
    queue_url = None

    def __init__(self, queue_name):
        self.queue_name = queue_name

    def client_factory(self):
        session = get_session()
        return session.create_client("sqs", region_name="us-east-1")

    async def get_queue_url(self):
        if self.queue_url:
            return self.queue_url
        else:
            async with self.client_factory() as client:
                queue_name = self.queue_name
                try:
                    response = await client.get_queue_url(QueueName=queue_name)
                except botocore.exceptions.ClientError as err:
                    if err.response["Error"]["Code"] == AwsErrorCodes.NON_EXISTENT_QUEUE:
                        print(f"Queue {queue_name} does not exist.")
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
                QueueUrl=queue_url, DelaySeconds=10, MessageBody=message_body_str
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
                                print(err)
                                print(
                                    f"Message {msg['ReceiptHandle']} was not able to be processed."
                                )

                except KeyboardInterrupt:
                    break
            print(f"Shutting down message handlers for queue {queue_name}")
            await client.close()


class DispatchQueue(Queuer):
    def __init__(self):
        super().__init__(settings.DISPATCH_QUEUE)

    async def run(self):
        print(f"Registering polling message handler for queue {self.queue_name}...")
        await self.poll_queue(self.message_handler)
        return self

    async def message_handler(self, client, msg):
        print(f'Got msg: {msg["Body"]}')


class UpdateWorkflowQueue(Queuer):
    def __init__(self):
        super().__init__(settings.DISPATCH_QUEUE)

    async def run(self):
        print(f"Registering polling message handler for queue {self.queue_name}...")
        await self.poll_queue(self.message_handler)
        return self

    async def message_handler(self, client, msg):
        print(f'Got msg: {msg["Body"]}')


class CreateScheduleQueue(Queuer):
    def __init__(self):
        super().__init__(settings.WORKFLOW_CREATE_SCHEDULE_QUEUE)

    async def run(self):
        print(f"Registering polling message handler for queue {self.queue_name}...")
        await self.poll_queue(self.message_handler)
        return self

    async def message_handler(self, client, msg):
        print(f'Got msg: {msg["Body"]}')
