import os
from subprocess import PIPE, CalledProcessError, Popen
from xmlrpc.client import Boolean

from covalent._file_transfer import File
from covalent._file_transfer.enums import FileSchemes, FileTransferStrategyTypes
from covalent._file_transfer.strategies.transfer_strategy_base import FileTransferStrategy


class Rsync(FileTransferStrategy):
    def __init__(self, user, host, private_key_path=None):

        self.user = user
        self.private_key_path = private_key_path
        self.host = host

        if self.private_key_path and not os.path.exists(self.private_key_path):
            raise FileNotFoundError(
                f"Provided private key ({self.private_key_path}) does not exist. Could not instantiate Rsync File Transfer Strategy. "
            )

    def get_rsync_ssh_cmd(
        self, local_file: File, remote_file: File, transfer_from_remote: bool = False
    ) -> str:
        local_filepath = str(local_file.filepath)
        remote_filepath = str(remote_file.filepath)
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

    def get_rsync_cmd(
        self, from_file: File, to_file: File, transfer_from_remote: bool = False
    ) -> str:
        from_filepath = str(from_file.filepath)
        to_filepath = str(to_file.filepath)
        args = ["rsync"]
        args.append(from_filepath)
        args.append(to_filepath)
        return " ".join(args)

    # move files in the local file system
    def move(self, from_file: File, to_file: File = File()) -> None:
        cmd = self.get_rsync_cmd(to_file, from_file)
        print(f"Running: {cmd}")
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if p.returncode != 0:
            raise CalledProcessError(p.returncode, f'"{cmd}" with error: {str(error)}')

    # download here implies 'from' is a remote source
    def download(self, from_file: File, to_file: File = File()) -> File:
        cmd = self.get_rsync_ssh_cmd(to_file, from_file, transfer_from_remote=True)
        print(f"Running: {cmd}")
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if p.returncode != 0:
            raise CalledProcessError(p.returncode, f'"{cmd}" with error: {str(error)}')
        return to_file

    # upload here implies 'to' is a remote source
    def upload(self, from_file: File, to_file: File) -> None:
        cmd = self.get_rsync_ssh_cmd(from_file, to_file, transfer_from_remote=False)
        print(f"Running: {cmd}")
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if p.returncode != 0:
            raise CalledProcessError(p.returncode, f'"{cmd}" with error: {str(error)}')
