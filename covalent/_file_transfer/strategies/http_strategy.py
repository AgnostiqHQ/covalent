import os
import urllib.request
from pathlib import Path
from subprocess import PIPE, CalledProcessError, Popen
from typing import Optional

from covalent._file_transfer import File
from covalent._file_transfer.strategies.transfer_strategy_base import FileTransferStrategy


class HTTP(FileTransferStrategy):
    """
    Implements Base FileTransferStrategy class to use HTTP to download files from public URLs.
    """

    # return callable to download here implies 'from' is a remote source
    def download(self, from_file: File, to_file: File = File()) -> File:
        from_filepath = from_file.uri
        to_filepath = to_file.filepath

        def callable():
            urllib.request.urlretrieve(from_filepath, to_filepath)

        return callable

    # HTTP Strategy is read only
    def upload(self, from_file: File, to_file: File = File()) -> File:
        raise NotImplementedError

    # HTTP Strategy is read only
    def cp(self, from_file: File, to_file: File = File()) -> File:
        raise NotImplementedError
