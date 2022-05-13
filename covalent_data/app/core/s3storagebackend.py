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

import logging
from abc import ABC
from http import client
from pathlib import Path
from typing import BinaryIO, Generator, List, Union

import boto3
import botocore.exceptions
from fastapi import HTTPException

from .storagebackend import StorageBackend

logger = logging.getLogger(__name__)


class S3StorageBackend(ABC):
    """Thin wrapper for S3 client

    Attributes:
        client: S3 client instance
        bucket_name: current working bucket name (default: "default")
    """

    def __init__(self, bucket_name="default"):
        self.bucket_name = bucket_name
        self.client = boto3.client("s3")

    def handle_client_error(self, e):
        err_code = e.response["Error"]["Code"]
        logger.warn(f"S3 Client Error: {err_code}")
        if err_code == "AccessDenied":
            raise HTTPException(
                401,
                detail="S3 client error: AccessDenied (Likely incorrect AWS credentials or configuration).",
            )
        else:
            raise HTTPException(400, detail=f"S3 client error: {err_code}")

    def get(self, bucket_name: str, object_name: str) -> Union[Generator[bytes, None, None], None]:
        """Get object from storage.

        Args:
            bucket_name: name of the bucket
            object_name: name of the object

        Returns:
            A generator yielding a byte stream or None if an
            error occurred in retrieving the object

        """

        try:
            resp = self.client.get_object(Bucket=bucket_name, Key=object_name)
        except (botocore.exceptions.ClientError) as e:
            # TODO: better logging
            logger.warn(f"Exception in S3 client when fetching object: {object_name}")
            self.handle_client_error(e)
            return None

        return resp["Body"]

    def put(
        self,
        data: BinaryIO,
        bucket_name: str,
        object_name: str,
        length: int,
        metadata: dict = None,
        overwrite: bool = False,
    ) -> (str, str):

        """Upload object to storage.

        Args:
            data: a binary file-like object
            bucket_name: name of the bucket
            object_name: name of the destination object
            length: number of bytes to upload
        Returns:
            (bucket_name, object_name) if write succeeds and ("", "") otherwise

        """

        try:
            res = self.client.put_object(
                Bucket=bucket_name, Key=object_name, ContentLength=length, Body=data
            )
        except (botocore.exceptions.ClientError) as e:
            # TODO: better logging
            logger.warn(f"Exception in S3 client when uploading object: {object_name}")
            self.handle_client_error(e)
            res = None

        if res:
            return (f"s3://{bucket_name}/{object_name}", object_name)
        else:
            return ("", "")

    def delete(self, bucket_name: str, object_names: List[str]):
        deleted_objects = []
        failed = []
        try:
            res = self.client.delete_objects(
                Bucket=bucket_name,
                Delete={
                    "Objects": list(map(lambda obj_name: {"Key": obj_name}, object_names)),
                    "Quiet": False,
                },
            )

            try:
                deleted_objects = res["Deleted"]
            except KeyError:
                deleted_objects = []

            try:
                failed = res["Errors"]
            except KeyError:
                failed = []

        except (botocore.exceptions.ClientError) as e:
            failed = object_names
            self.handle_client_error(e)

        deleted_objects = list(map(lambda obj_metadata: obj_metadata["Key"], deleted_objects))
        failed = list(map(lambda obj_metadata: obj_metadata["Key"], failed))

        return deleted_objects, failed
