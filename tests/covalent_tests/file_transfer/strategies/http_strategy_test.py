import pytest

from covalent._file_transfer import File
from covalent._file_transfer.strategies.http_strategy import HTTP


class TestHTTPStrategy:

    MOCK_LOCAL_FILEPATH = "/Users/user/data.csv"
    MOCK_REMOTE_FILEPATH = "http://example.com/data.csv"

    def test_download(self, mocker):
        # validate urlretrieve called with appropriate arguments
        urlretrieve_mock = mocker.patch("urllib.request.urlretrieve")
        from_file = File(self.MOCK_REMOTE_FILEPATH)
        to_file = File(self.MOCK_LOCAL_FILEPATH)
        HTTP().download(from_file, to_file)()
        urlretrieve_mock.assert_called_with(from_file.uri, to_file.filepath)

    @pytest.mark.parametrize(
        "operation",
        [
            ("cp"),
            ("upload"),
        ],
    )
    def test_upload_cp_failure(self, operation, mocker):
        with pytest.raises(NotImplementedError):
            if operation == "upload":
                HTTP().upload(File(self.MOCK_REMOTE_FILEPATH), File(self.MOCK_LOCAL_FILEPATH))()
            elif operation == "cp":
                HTTP().cp(File(self.MOCK_REMOTE_FILEPATH), File(self.MOCK_LOCAL_FILEPATH))()
