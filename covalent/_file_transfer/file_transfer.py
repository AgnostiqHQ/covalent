import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

from furl import furl

from covalent._file_transfer.enums import FileSchemes, Order
from covalent._file_transfer.file import File
from covalent._file_transfer.strategies.transfer_strategy_base import FileTransferStrategy

if TYPE_CHECKING:
    pass


class FileTransfer:
    def __init__(
        self,
        from_file: Optional[Union[File, str]] = None,
        to_file: Optional[Union[File, str]] = None,
        order: Order = Order.BEFORE,
        strategy: Optional[FileTransferStrategy] = None,
    ) -> None:

        if isinstance(from_file, str) or from_file is None:
            from_file = File(from_file)
        elif not isinstance(from_file, File):
            raise AttributeError(
                "Covalent FileTransfer requires files to be either of type File, string, or None."
            )

        if isinstance(to_file, str) or to_file is None:
            to_file = File(to_file)
        elif not isinstance(to_file, File):
            raise AttributeError(
                "Covalent FileTransfer requires files to be either of type File, string, or None."
            )

        self.to_file = to_file
        self.from_file = from_file
        self.strategy = strategy
        self.order = order

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


def TransferFromRemote(
    from_filepath: str,
    to_filepath: Union[str, None] = None,
    strategy: Union[FileTransferStrategy, None] = None,
):
    # override is_remote for the case where from_filepath is of a file:// scheme where the file is remote (rsync ssh)
    from_file = File(from_filepath, is_remote=True)
    return FileTransfer(
        from_filepath=from_file, to_filepath=to_filepath, order=Order.BEFORE, strategy=strategy
    )


def TransferToRemote(
    to_filepath: str,
    from_filepath: Union[str, None] = None,
    strategy: Union[FileTransferStrategy, None] = None,
):
    # override is_remote for the case where to_filepath is of a file:// scheme where the file is remote (rsync ssh)
    to_file = File(to_filepath, is_remote=True)
    return FileTransfer(
        from_filepath=from_filepath, to_filepath=to_file, order=Order.AFTER, strategy=strategy
    )
