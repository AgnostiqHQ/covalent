import pytest

from covalent._file_transfer import File
from covalent._file_transfer.strategies.s3_strategy import S3

from furl import furl

class TestS3Strategy:

    MOCK_LOCAL_FILEPATH = "/Users/user/data.csv"
    MOCK_REMOTE_FILEPATH = "s3://covalent-tmp/data.csv"

    def test_download(self, mocker):
        # validate urlretrieve called with appropriate arguments
        boto3_mock = mocker.patch("boto3.client")
        boto3_mock.download_file.return_value = None

        from_file = File(self.MOCK_REMOTE_FILEPATH)
        to_file = File(self.MOCK_LOCAL_FILEPATH)

        bucket_name = furl(from_file.uri).origin[5:]

        S3().download(from_file, to_file)()

        boto3_mock().download_file.assert_called_with(bucket_name, from_file.filepath, to_file.filepath)

    def test_upload(self, mocker):
        # validate urlretrieve called with appropriate arguments
        boto3_mock = mocker.patch("boto3.client")
        boto3_mock.upload_file.return_value = None

        to_file = File(self.MOCK_REMOTE_FILEPATH)
        from_file = File(self.MOCK_LOCAL_FILEPATH)

        bucket_name = furl(to_file.uri).origin[5:]

        S3().upload(from_file, to_file)()

        boto3_mock().upload_file.assert_called_with(from_file.filepath,bucket_name, to_file.filepath)


    def test_cp_failure(self, mocker):
        with pytest.raises(NotImplementedError):
            S3().cp(File(self.MOCK_REMOTE_FILEPATH), File(self.MOCK_LOCAL_FILEPATH))()
