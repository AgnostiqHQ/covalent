from os.path import exists
from subprocess import PIPE, Popen

from covalent._file_transfer import File
from covalent._file_transfer.enums import FileSchemes
from covalent._file_transfer.strategies.transfer_strategy_base import FileTransferStrategy


class Rsync(FileTransferStrategy):
    def __init__(self, user, host, private_key_path=None):
        self.user = user
        self.private_key_path = private_key_path
        self.host = host
        self.supported_scheme = FileSchemes.File

        if self.private_key_path and not exists(self.private_key_path):
            raise FileNotFoundError(
                f"Provided private key ({self.private_key_path}) does not exist. Could not instantiate Rsync File Transfer Strategy. "
            )

    def get_rsync_cmd(self, file: File, transfer_from_remote: bool = False) -> str:
        local_filepath = str(file.local_filepath)
        remote_filepath = str(file.remote_filepath)
        args = ["rsync"]
        if self.private_key_path:
            args.append(f'-e "ssh -i {self.private_key_path}"')
        else:
            args.append("-e ssh")

        remote_source = f"{self.user}@{self.host}:{remote_filepath}"

        if transfer_from_remote:
            args.append(remote_source)
            args.append(local_filepath)
        else:
            args.append(local_filepath)
            args.append(remote_source)

        return " ".join(args)

    def download(self, file: File):
        cmd = self.get_rsync_cmd(file, transfer_from_remote=True)
        print(f"Running: {cmd}")
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if p.returncode != 0:
            print(f"There was an error downloading file {file.local_filepath}")
            print(f"Return code: {p.returncode}")
            print(f"Output: {output}")
            print(f"Error: {error}")

    def upload(self, file: File):
        cmd = self.get_rsync_cmd(file)
        print(f"Running: {cmd}")
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if p.returncode != 0:
            print(f"There was an error uploading file {file.local_filepath}")
            print(f"Return code: {p.returncode}")
            print(f"Output: {output}")
            print(f"Error: {str(error)}")
