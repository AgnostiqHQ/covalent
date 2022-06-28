import pytest

from covalent._file_transfer import File
from covalent._file_transfer.strategies.rsync_strategy import Rsync


class TestRsyncStrategy:
    MOCK_HOST = "11.11.11.11"
    MOCK_USER = "admin"
    MOCK_REMOTE_FILEPATH = "/home/ubuntu/observations.csv"

    def test_get_rsync_cmd(self):
        file = File(remote_path=self.MOCK_REMOTE_FILEPATH)
        upload_cmd = Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).get_rsync_cmd(
            file, transfer_from_remote=False
        )
        download_cmd = Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).get_rsync_cmd(
            file, transfer_from_remote=True
        )
        assert (
            upload_cmd
            == f"rsync -e ssh /tmp/{file.id} {self.MOCK_USER}@{self.MOCK_HOST}:{self.MOCK_REMOTE_FILEPATH}"
        )
        assert (
            download_cmd
            == f"rsync -e ssh {self.MOCK_USER}@{self.MOCK_HOST}:{self.MOCK_REMOTE_FILEPATH} /tmp/{file.id}"
        )
