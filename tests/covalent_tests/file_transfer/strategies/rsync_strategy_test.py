from subprocess import CalledProcessError
from unittest.mock import Mock

import pytest

from covalent._file_transfer import File
from covalent._file_transfer.strategies.rsync_strategy import Rsync


class TestRsyncStrategy:

    MOCK_HOST = "11.11.11.11"
    MOCK_USER = "admin"
    MOCK_LOCAL_FILEPATH = "/Users/user/data.csv"
    MOCK_PRIVATE_KEY_PATH = "/Users/user/.ssh/id_rsa"
    MOCK_REMOTE_FILEPATH = "/home/ubuntu/observations.csv"

    @pytest.mark.parametrize(
        "is_upload",
        [
            (True),
            (False),
        ],
    )
    def test_upload_download_success(self, is_upload, mocker):

        MOCK_CMD = "rsync ..."
        Popen = Mock()
        Popen.communicate.return_value = ("", "")
        Popen.returncode = 0
        popen_mock = mocker.patch(
            "covalent._file_transfer.strategies.rsync_strategy.Popen", return_value=Popen
        )
        mocker.patch(
            "covalent._file_transfer.strategies.rsync_strategy.Rsync.get_rsync_cmd",
            return_value=MOCK_CMD,
        )
        if is_upload:
            Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).upload(File("/tmp/data.csv"))
        else:
            Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).download(File("/tmp/data.csv"))
        popen_mock.assert_called_once()

    @pytest.mark.parametrize(
        "is_upload",
        [
            (True),
            (False),
        ],
    )
    def test_upload_download_failure(self, is_upload, mocker):

        MOCK_CMD = "rsync ..."
        Popen = Mock()
        Popen.communicate.return_value = ("", "syntax or usage error (code 1)")
        Popen.returncode = 1
        mocker.patch("covalent._file_transfer.strategies.rsync_strategy.Popen", return_value=Popen)
        mocker.patch(
            "covalent._file_transfer.strategies.rsync_strategy.Rsync.get_rsync_cmd",
            return_value=MOCK_CMD,
        )

        with pytest.raises(CalledProcessError):
            if is_upload:
                Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).upload(File("/tmp/data.csv"))
            else:
                Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).download(File("/tmp/data.csv"))

    @pytest.mark.parametrize(
        "is_remote_file, is_private_key_defined",
        [
            (True, True),
            (False, False),
            (True, False),
            (False, True),
        ],
    )
    def test_get_rsync_cmd(self, is_remote_file, is_private_key_defined, mocker):

        mocker.patch("os.path.exists", return_value=True)
        if is_remote_file:
            file = File(remote_path=self.MOCK_REMOTE_FILEPATH)
            local_path = f"/tmp/{file.id}"
            remote_path = self.MOCK_REMOTE_FILEPATH
        else:
            file = File(self.MOCK_LOCAL_FILEPATH)
            local_path = self.MOCK_LOCAL_FILEPATH
            remote_path = f"/tmp/{file.id}"

        if is_private_key_defined:
            ssh_setting = f'"ssh -i {self.MOCK_PRIVATE_KEY_PATH}"'
            private_key_path = self.MOCK_PRIVATE_KEY_PATH
        else:
            ssh_setting = "ssh"
            private_key_path = None

        upload_cmd = Rsync(
            user=self.MOCK_USER, host=self.MOCK_HOST, private_key_path=private_key_path
        ).get_rsync_cmd(file, transfer_from_remote=False)
        download_cmd = Rsync(
            user=self.MOCK_USER, host=self.MOCK_HOST, private_key_path=private_key_path
        ).get_rsync_cmd(file, transfer_from_remote=True)
        assert (
            upload_cmd
            == f"rsync -e {ssh_setting} {local_path} {self.MOCK_USER}@{self.MOCK_HOST}:{remote_path}"
        )
        assert (
            download_cmd
            == f"rsync -e {ssh_setting} {self.MOCK_USER}@{self.MOCK_HOST}:{remote_path} {local_path}"
        )
