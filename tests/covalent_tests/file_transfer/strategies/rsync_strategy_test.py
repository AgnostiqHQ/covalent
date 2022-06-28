import pytest

from covalent._file_transfer import File
from covalent._file_transfer.strategies.rsync_strategy import Rsync


class TestRsyncStrategy:
    def test_get_rsync_cmd(self):
        file = File(remote_path="/home/ubuntu/observations.csv")
        upload_cmd = Rsync(user="admin", host="11.11.11.11").get_rsync_cmd(
            file, transfer_from_remote=False
        )
        download_cmd = Rsync(user="admin", host="11.11.11.11").get_rsync_cmd(
            file, transfer_from_remote=True
        )
        assert (
            upload_cmd
            == f"rsync -e ssh /tmp/{file.id} admin@11.11.11.11:/home/ubuntu/observations.csv"
        )
        assert (
            download_cmd
            == f"rsync -e ssh admin@11.11.11.11:/home/ubuntu/observations.csv /tmp/{file.id}"
        )
