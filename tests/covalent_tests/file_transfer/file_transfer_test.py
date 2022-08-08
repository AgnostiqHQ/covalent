from pathlib import Path
from unittest.mock import Mock

import pytest

from covalent._file_transfer import File
from covalent._file_transfer.enums import FileSchemes, FileTransferStrategyTypes
from covalent._file_transfer.file_transfer import FileTransfer


class TestFileTransfer:
    def test_raise_exception_valid_args(self):
        # valid filepaths should not raise errors
        FileTransfer("file:///home/one.csv", "file:///home/one.csv")
        FileTransfer("file:///home/one.csv", None)
        FileTransfer(None, "file:///home/one.csv")
        FileTransfer(None, None)
        FileTransfer(File("file:///home/one.csv"), "file:///home/one.csv")
        FileTransfer("file:///home/one.csv", File("file:///home/one.csv"))
        FileTransfer(File("file:///home/one.csv"), File("file:///home/one.csv"))

    @pytest.mark.parametrize(
        "is_from_file_remote, is_to_file_remote",
        [
            (False, False),
            (True, False),
            (False, True),
        ],
    )
    def test_upload_download_cp(self, is_from_file_remote, is_to_file_remote):
        from_file = File("file:///home/source.csv", is_remote=is_from_file_remote)
        to_file = File("file:///home/dest.csv", is_remote=is_to_file_remote)

        mock_strategy = Mock()

        ft = FileTransfer(from_file, to_file, strategy=mock_strategy)

        ft.cp()

        if not is_to_file_remote and not is_from_file_remote:
            mock_strategy.cp.assert_called_once()
        elif is_from_file_remote and not is_to_file_remote:
            mock_strategy.download.assert_called_once()
        elif not is_from_file_remote and is_to_file_remote:
            mock_strategy.upload.assert_called_once()
