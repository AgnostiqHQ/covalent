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

import os

from furl import furl

from ..._shared_files import logger
from .. import File
from .transfer_strategy_base import FileTransferStrategy

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class S3(FileTransferStrategy):

    """
    Implements Base FileTransferStrategy class to upload/download files from S3 Bucket.
    """

    def __init__(
        self,
        credentials: str = os.environ.get("AWS_SHARED_CREDENTIALS_FILE")
        or os.path.join(os.environ["HOME"], ".aws/credentials"),
        profile: str = os.environ.get("AWS_PROFILE") or None,
        region_name: str = os.getenv("AWS_REGION") or None,
    ):

        self.credentials = credentials
        self.profile = profile
        self.region_name = region_name

        try:
            import boto3
        except ImportError:
            raise ImportError(
                "Using S3 strategy requires boto3 from AWS installed on your system."
            )

        os.environ["AWS_SHARED_CREDENTIALS_FILE"] = self.credentials
        if self.profile is not None:
            os.environ["AWS_PROFILE"] = self.profile

        # AWS Account Retrieval
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        account = identity.get("Account")

        if account is None:
            raise Exception("Incorrect AWS account credentials")

    # return callable to download here implies 'from' is a remote source
    def download(self, from_file: File, to_file: File = File()) -> File:
        """Download files or the contents of folders from S3 bucket."""
        app_log.debug(f"Is dir: {from_file._is_dir}")

        from_filepath = from_file.filepath
        to_filepath = to_file.filepath

        if from_filepath.startswith("/"):
            from_filepath = from_filepath[1:]

        bucket_name = furl(from_file.uri).origin[5:]
        app_log.debug(
            f"S3 download bucket: {bucket_name}, from_filepath: {from_filepath}, to_filepath {to_filepath}."
        )

        if from_file._is_dir:

            def callable():
                """Download files from a folder in s3 bucket."""
                from pathlib import Path

                import boto3

                s3 = boto3.client(
                    "s3",
                    region_name=self.region_name,
                )

                for obj_metadata in s3.list_objects(Bucket=bucket_name, Prefix=from_filepath)[
                    "Contents"
                ]:
                    obj_key = obj_metadata["Key"]
                    obj_destination_filepath = Path(to_filepath) / obj_key
                    if not obj_key.endswith("/"):
                        obj_destination_filepath.parents[0].mkdir(parents=True, exist_ok=True)
                        app_log.debug(
                            f"Downloading file {str(Path(from_filepath) / obj_key)} to {str(obj_destination_filepath)}."
                        )
                        s3.download_file(
                            bucket_name,
                            str(Path(from_filepath) / obj_key),
                            str(obj_destination_filepath),
                        )

        else:

            def callable():
                """Download file from s3 bucket."""
                import boto3

                s3 = boto3.client(
                    "s3",
                    region_name=self.region_name,
                )
                s3.download_file(bucket_name, from_filepath, to_filepath)

        return callable

    # return callable to download here implies 'to' is a remote source
    def upload(self, from_file: File, to_file: File = File()) -> File:
        """Upload files or folders to S3 bucket."""
        from_filepath = from_file.filepath
        to_filepath = to_file.filepath

        if to_filepath.startswith("/"):
            to_filepath = to_filepath.strip("/")

        bucket_name = furl(to_file.uri).origin[5:]
        app_log.debug(
            f"S3 upload bucket: {bucket_name}, from_filepath: {from_filepath}, to_filepath {to_filepath}."
        )

        if from_file._is_dir:

            def callable():
                """List and upload files from a directory to the remote S3 bucket."""
                import os
                from pathlib import Path

                import boto3

                s3 = boto3.client(
                    "s3",
                    region_name=self.region_name,
                )

                for dir_, _, files in os.walk(from_filepath):
                    for file_name in files:
                        rel_dir = os.path.relpath(dir_, from_filepath)
                        rel_file = os.path.join(rel_dir, file_name)
                        obj_from_filepath = str(Path(from_filepath) / rel_file)
                        obj_to_filepath = str(Path(to_filepath) / rel_file)
                        app_log.debug(f"Uploading from {obj_from_filepath} to {obj_to_filepath}.")
                        s3.upload_file(obj_from_filepath, bucket_name, obj_to_filepath)

        else:

            def callable():
                """Upload file to remote S3 bucket."""
                import boto3

                s3 = boto3.client(
                    "s3",
                    region_name=self.region_name,
                )
                s3.upload_file(from_filepath, bucket_name, to_filepath)

        return callable

    # No S3 Strategy for copy
    def cp(self, from_file: File, to_file: File = File()) -> File:
        raise NotImplementedError
