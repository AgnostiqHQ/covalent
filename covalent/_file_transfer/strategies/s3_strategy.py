import os

from furl import furl

from .. import File
from .transfer_strategy_base import FileTransferStrategy


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
        from_filepath = from_file.filepath
        to_filepath = to_file.filepath
        bucket_name = furl(from_file.uri).origin[5:]

        def callable():
            import boto3

            s3 = boto3.client(
                "s3",
                region_name=self.region_name,
            )
            s3.download_file(bucket_name, from_filepath, to_filepath)

        return callable

    # return callable to download here implies 'to' is a remote source
    def upload(self, from_file: File, to_file: File = File()) -> File:

        from_filepath = from_file.filepath
        to_filepath = to_file.filepath
        bucket_name = furl(to_file.uri).origin[5:]

        def callable():
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
