import os
import sys
from unittest.mock import MagicMock

import pytest
from furl import furl

from covalent._file_transfer import File
from covalent._file_transfer.strategies.s3_strategy import S3


class TestS3Strategy:

    MOCK_LOCAL_FILEPATH = "/Users/user/data.csv"
    MOCK_REMOTE_FILEPATH = "s3://covalent-tmp/data.csv"
    MOCK_AWS_CREDENTIALS = "~/.aws/credentials"
    MOCK_AWS_PROFILE = "default"
    MOCK_AWS_REGION = "us-east-1"

    def test_init(self, mocker):
        # test S3 init fails due to not having boto3
        with pytest.raises(ImportError):
            strategy = S3()

        # test with boto3 module defined and failure resolving aws credentials
        boto3_mock = MagicMock()
        sys.modules["boto3"] = boto3_mock
        boto3_client_mock = mocker.patch("boto3.client")
        boto3_client_mock().get_caller_identity().get.return_value = None
        with pytest.raises(Exception):
            strategy = S3()

        # test with boto3 module defined and successfully resolving aws credentials - success initating S3 strategy
        account_mock = MagicMock()
        boto3_client_mock().get_caller_identity().get.return_value = account_mock
        strategy = S3(self.MOCK_AWS_CREDENTIALS, self.MOCK_AWS_PROFILE, self.MOCK_AWS_REGION)
        assert os.environ["AWS_SHARED_CREDENTIALS_FILE"] == self.MOCK_AWS_CREDENTIALS
        assert os.environ["AWS_PROFILE"] == self.MOCK_AWS_PROFILE

    def test_download(self, mocker):
        # validate boto3.client('s3').download_file is called with appropriate arguments

        boto3_mock = MagicMock()
        sys.modules["boto3"] = boto3_mock

        boto3_client_mock = mocker.patch("boto3.client")
        boto3_client_mock.download_file.return_value = None

        from_file = File(self.MOCK_REMOTE_FILEPATH)
        to_file = File(self.MOCK_LOCAL_FILEPATH)

        bucket_name = furl(from_file.uri).origin[5:]

        S3().download(from_file, to_file)()

        boto3_client_mock().download_file.assert_called_with(
            bucket_name, from_file.filepath, to_file.filepath
        )

    def test_upload(self, mocker):
        # validate boto3.client('s3').upload_file is called with appropriate arguments

        boto3_mock = MagicMock()
        sys.modules["boto3"] = boto3_mock

        boto3_client_mock = mocker.patch("boto3.client")
        boto3_client_mock.download_file.return_value = None

        to_file = File(self.MOCK_REMOTE_FILEPATH)
        from_file = File(self.MOCK_LOCAL_FILEPATH)

        bucket_name = furl(to_file.uri).origin[5:]

        S3().upload(from_file, to_file)()

        boto3_client_mock().upload_file.assert_called_with(
            from_file.filepath, bucket_name, to_file.filepath
        )

    def test_cp_failure(self, mocker):

        mock_boto3 = MagicMock()
        sys.modules["boto3"] = mock_boto3

        with pytest.raises(NotImplementedError):
            S3().cp(File(self.MOCK_REMOTE_FILEPATH), File(self.MOCK_LOCAL_FILEPATH))()
