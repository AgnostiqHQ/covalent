import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

from furl import furl

from covalent._file_transfer.enums import FileSchemes, TransferTypes
from covalent._file_transfer.file import File
from covalent._file_transfer.strategies.transfer_strategy_base import FileTransferStrategy

if TYPE_CHECKING:
    pass


class FileTransfer:
    def __init__(
        self,
        from_filepath: Union[str, None],
        to_filepath: Union[str, None],
        transfer_type: TransferTypes = TransferTypes.BEFORE,
        strategy: Union[FileTransferStrategy, None] = None,
    ) -> None:

        self.from_file = File(from_filepath)
        self.to_file = File(to_filepath)
        self.strategy = strategy

        # this is currently the case but as we further develop file transfer strategies we may support this
        # for example we may support streaming files between buckets in S3
        if self.from_file.is_remote and self.to_file.is_remote:
            raise ValueError(
                "Covalent currently does not support remote->remote file transfers, please update from_filepath or to_filepath to correspond to a local filepath."
            )

    def move(self):
        # LOCAL -> LOCAL
        if not self.from_file.is_remote and not self.to_file.is_remote:
            return self.strategy.move(self.from_file, self.to_file)
        # LOCAL -> REMOTE
        if not self.from_file.is_remote and self.to_file.is_remote:
            return self.strategy.upload(self.from_file, self.to_file)
        # REMOTE -> LOCAL
        if self.from_file.is_remote and not self.to_file.is_remote:
            return self.strategy.download(self.from_file, self.to_file)
        # REMOTE -> REMOTE
        if self.from_file.is_remote and self.to_file.is_remote:
            self.strategy.move(self.from_file, self.to_file)


# Factories


def TransferFrom(from_filepath: str, to_filepath: Union[str, None] = None):
    return FileTransfer(
        from_filepath=from_filepath, to_filepath=to_filepath, transfer_type=TransferTypes.BEFORE
    )


def TransferTo(to_filepath: str, from_filepath: Union[str, None] = None):
    return FileTransfer(
        from_filepath=from_filepath, to_filepath=to_filepath, transfer_type=TransferTypes.AFTER
    )
