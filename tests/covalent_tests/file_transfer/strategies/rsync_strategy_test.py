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
        "operation",
        [
            ("download"),
            ("upload"),
            ("cp"),
        ],
    )
    def test_upload_download_success(self, operation, mocker):

        # validate subprocess created by instantiating Popen

        MOCK_CMD = "rsync ..."
        Popen = Mock()
        Popen.communicate.return_value = ("", "")
        Popen.returncode = 0
        popen_mock = mocker.patch(
            "covalent._file_transfer.strategies.rsync_strategy.Popen", return_value=Popen
        )
        mocker.patch(
            "covalent._file_transfer.strategies.rsync_strategy.Rsync.get_rsync_ssh_cmd",
            return_value=MOCK_CMD,
        )
        if operation == "upload":
            Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).upload(
                File("/tmp/source.csv"), File("/tmp/dest.csv")
            )()
        elif operation == "download":
            Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).download(
                File("/tmp/source.csv"), File("/tmp/dest.csv")
            )()
        elif operation == "cp":
            Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).cp(
                File("/tmp/source.csv"), File("/tmp/dest.csv")
            )()

        popen_mock.assert_called_once()

    @pytest.mark.parametrize(
        "operation",
        [
            ("download"),
            ("upload"),
            ("cp"),
        ],
    )
    def test_upload_download_cp_failure(self, operation, mocker):

        # if subprocess returns with return code 1 raise a CalledProcessError exception

        MOCK_CMD = "rsync ..."
        Popen = Mock()
        Popen.communicate.return_value = ("", "syntax or usage error (code 1)")
        Popen.returncode = 1
        mocker.patch("covalent._file_transfer.strategies.rsync_strategy.Popen", return_value=Popen)
        mocker.patch(
            "covalent._file_transfer.strategies.rsync_strategy.Rsync.get_rsync_ssh_cmd",
            return_value=MOCK_CMD,
        )

        with pytest.raises(CalledProcessError):
            if operation == "upload":
                Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).upload(
                    File("/tmp/source.csv"), File("/tmp/dest.csv")
                )()
            elif operation == "download":
                Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).download(
                    File("/tmp/source.csv"), File("/tmp/dest.csv")
                )()
            elif operation == "cp":
                Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).cp(
                    File("/tmp/source.csv"), File("/tmp/dest.csv")
                )()

    def test_get_rsync_cmd(self):
        from_file = File("/home/ubuntu/from.csv")
        to_file = File("/home/ubuntu/to.csv")

        cp_cmd = Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).get_rsync_cmd(from_file, to_file)

        # command takes the form of rsync [source] [destination]
        assert cp_cmd == "rsync -a /home/ubuntu/from.csv /home/ubuntu/to.csv"

    def test_get_ssh_rsync_cmd_with_ssh_key(self, mocker):

        mocker.patch("os.path.exists", return_value=True)

        local_file = File(self.MOCK_LOCAL_FILEPATH)
        remote_file = File(self.MOCK_REMOTE_FILEPATH)
        private_key_path = self.MOCK_PRIVATE_KEY_PATH

        upload_cmd_with_key = Rsync(
            user=self.MOCK_USER, host=self.MOCK_HOST, private_key_path=private_key_path
        ).get_rsync_ssh_cmd(local_file, remote_file, transfer_from_remote=False)

        upload_cmd_without_key = Rsync(user=self.MOCK_USER, host=self.MOCK_HOST).get_rsync_ssh_cmd(
            local_file, remote_file, transfer_from_remote=False
        )

        download_cmd_with_key = Rsync(
            user=self.MOCK_USER, host=self.MOCK_HOST, private_key_path=private_key_path
        ).get_rsync_ssh_cmd(local_file, remote_file, transfer_from_remote=True)

        download_cmd_without_key = Rsync(
            user=self.MOCK_USER, host=self.MOCK_HOST
        ).get_rsync_ssh_cmd(local_file, remote_file, transfer_from_remote=True)

        # commands take the form of rsync -s ssh ... [source] [destination]
        assert (
            upload_cmd_with_key
            == f'rsync -e "ssh -i {private_key_path}" {self.MOCK_LOCAL_FILEPATH} {self.MOCK_USER}@{self.MOCK_HOST}:{self.MOCK_REMOTE_FILEPATH}'
        )
        assert (
            download_cmd_with_key
            == f'rsync -e "ssh -i {private_key_path}" {self.MOCK_USER}@{self.MOCK_HOST}:{self.MOCK_REMOTE_FILEPATH} {self.MOCK_LOCAL_FILEPATH}'
        )

        assert (
            upload_cmd_without_key
            == f"rsync -e ssh {self.MOCK_LOCAL_FILEPATH} {self.MOCK_USER}@{self.MOCK_HOST}:{self.MOCK_REMOTE_FILEPATH}"
        )
        assert (
            download_cmd_without_key
            == f"rsync -e ssh {self.MOCK_USER}@{self.MOCK_HOST}:{self.MOCK_REMOTE_FILEPATH} {self.MOCK_LOCAL_FILEPATH}"
        )
