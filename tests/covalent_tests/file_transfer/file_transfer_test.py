from pathlib import Path
from unittest.mock import Mock

import pytest

from covalent._file_transfer import File
from covalent._file_transfer.enums import FileSchemes, FileTransferStrategyTypes
from covalent._file_transfer.file_transfer import FileTransfer


class TestFile:
    """Test FileTransfer object methods"""

    def test_raise_exception_invalid_args(self):
        # valid filepaths should not raise errors
        FileTransfer("file:///home/one.csv", "file:///home/one.csv")
        FileTransfer("file:///home/one.csv", None)
        FileTransfer(None, "file:///home/one.csv")
        FileTransfer(None, None)
        FileTransfer(File("file:///home/one.csv"), "file:///home/one.csv")
        FileTransfer("file:///home/one.csv", File("file:///home/one.csv"))
        FileTransfer(File("file:///home/one.csv"), File("file:///home/one.csv"))
