# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

import os
from subprocess import PIPE, CalledProcessError, Popen
from typing import Optional

from .. import File
from .transfer_strategy_base import FileTransferStrategy


class Rsync(FileTransferStrategy):
    """
    Implements Base FileTransferStrategy class to use rsync to move files to and from remote or local filesystems. Rsync via ssh is used if one of the provided files is marked as remote.

    Attributes:
        user: (optional) Determine user to specify for remote host if using rsync with ssh
        host: (optional) Determine what host to connect to if using rsync with ssh
        private_key_path: (optional) Filepath for ssh private key to use if using rsync with ssh
    """

    def __init__(
        self,
        user: Optional[str] = "",
        host: Optional[str] = "",
        private_key_path: Optional[str] = None,
    ):

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
        local_filepath = local_file.filepath
        remote_filepath = remote_file.filepath
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
        from_filepath = from_file.filepath
        to_filepath = to_file.filepath
        return f"rsync -a {from_filepath} {to_filepath}"

    def return_subprocess_callable(self, cmd) -> None:
        def callable():
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            output, error = p.communicate()
            if p.returncode != 0:
                raise CalledProcessError(p.returncode, f'"{cmd}" with error: {str(error)}')

        return callable

    # return callable to move files in the local file system
    def cp(self, from_file: File, to_file: File = File()) -> None:
        cmd = self.get_rsync_cmd(from_file, to_file)
        return self.return_subprocess_callable(cmd)

    # return callable to download here implies 'from' is a remote source
    def download(self, from_file: File, to_file: File = File()) -> File:
        cmd = self.get_rsync_ssh_cmd(to_file, from_file, transfer_from_remote=True)
        return self.return_subprocess_callable(cmd)

    # return callable to upload here implies 'to' is a remote source
    def upload(self, from_file: File, to_file: File) -> None:
        cmd = self.get_rsync_ssh_cmd(from_file, to_file, transfer_from_remote=False)
        return self.return_subprocess_callable(cmd)
