import pytest
from furl import furl

from covalent._file_transfer import File
from covalent._file_transfer.strategies.s3_strategy import S3

from unittest.mock import MagicMock

import sys

class TestS3Strategy:

    MOCK_LOCAL_FILEPATH = "/Users/user/data.csv"
    MOCK_REMOTE_FILEPATH = "s3://covalent-tmp/data.csv"

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
