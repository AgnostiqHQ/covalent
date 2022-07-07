import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

from furl import furl

from covalent._file_transfer.enums import FileSchemes, FileTransferStrategyTypes, Order
from covalent._file_transfer.file import File
from covalent._file_transfer.strategies.http_strategy import HTTP
from covalent._file_transfer.strategies.rsync_strategy import Rsync
from covalent._file_transfer.strategies.transfer_strategy_base import FileTransferStrategy


class FileTransfer:
    """
    FileTransfer object class that takes two File Objects (from, to) and a File Transfer Strategy to perform remote or local filesystem operations.

    Attributes:
        from_file: File path corresponding to the source file.
        to_file: File path corresponding to the destination file.
        order: Order to execute the file transfer, BEFORE electron execution or AFTER.
        strategy: File Transfer Strategy to perform file operations.
    """

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
                "FileTransfer() requires files to be either of type File, string, or None."
            )

        if isinstance(to_file, str) or to_file is None:
            to_file = File(to_file)
        elif not isinstance(to_file, File):
            raise AttributeError(
                "FileTransfer requires files to be either of type File, string, or None."
            )

        # assign explicit strategy or default to strategy based on from_file & to_file schemes
        if strategy:
            self.strategy = strategy
        elif (
            from_file.mapped_strategy_type == FileTransferStrategyTypes.Rsync
            and to_file.mapped_strategy_type == FileTransferStrategyTypes.Rsync
        ):
            self.strategy = Rsync()
        elif from_file.mapped_strategy_type == FileTransferStrategyTypes.HTTP:
            self.strategy = HTTP()
        else:
            raise AttributeError("FileTransfer requires a file transfer strategy to be specified")

        self.to_file = to_file
        self.from_file = from_file
        self.order = order

        # this is currently the case but as we further develop file transfer strategies we may support this
        # for example we may support streaming files between buckets in S3
        if self.from_file.is_remote and self.to_file.is_remote:
            raise ValueError(
                "FileTransfer currently does not support remote->remote file transfers, please update from_filepath or to_filepath to correspond to a local filepath."
            )

    def cp(self):
        # local -> local or remote -> remote
        if (not self.from_file.is_remote and not self.to_file.is_remote) or (
            self.from_file.is_remote and self.to_file.is_remote
        ):
            return self.strategy.cp(self.from_file, self.to_file)
        # local -> remote
        if not self.from_file.is_remote and self.to_file.is_remote:
            return self.strategy.upload(self.from_file, self.to_file)
        # remote -> local
        if self.from_file.is_remote and not self.to_file.is_remote:
            return self.strategy.download(self.from_file, self.to_file)


# Factories


def TransferFromRemote(
    from_filepath: str,
    to_filepath: Union[str, None] = None,
    strategy: Union[FileTransferStrategy, None] = None,
):
    # override is_remote for the case where from_filepath is of a file:// scheme where the file is remote (rsync ssh)
    from_file = File(from_filepath, is_remote=True)
    return FileTransfer(
        from_file=from_file, to_file=to_filepath, order=Order.BEFORE, strategy=strategy
    )


def TransferToRemote(
    to_filepath: str,
    from_filepath: Union[str, None] = None,
    strategy: Union[FileTransferStrategy, None] = None,
):
    # override is_remote for the case where to_filepath is of a file:// scheme where the file is remote (rsync ssh)
    to_file = File(to_filepath, is_remote=True)
    return FileTransfer(
        from_file=from_filepath, to_file=to_file, order=Order.AFTER, strategy=strategy
    )
