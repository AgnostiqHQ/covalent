# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional, Union

from .enums import FileTransferStrategyTypes, FtCallDepReturnValue, Order
from .file import File
from .strategies.gcloud_strategy import GCloud
from .strategies.http_strategy import HTTP
from .strategies.s3_strategy import S3
from .strategies.shutil_strategy import Shutil
from .strategies.transfer_strategy_base import FileTransferStrategy

# TODO: make this pluggable similar to executor plugins
_strategy_type_map = {
    FileTransferStrategyTypes.Shutil: Shutil,
    FileTransferStrategyTypes.S3: S3,
    FileTransferStrategyTypes.HTTP: HTTP,
    FileTransferStrategyTypes.GCloud: GCloud,
}


def _guess_transfer_strategy(from_file: File, to_file: File) -> FileTransferStrategy:
    # Handle the following cases automatically
    # Local-Remote (except HTTP destination)
    # Remote-local
    # Local-local

    if (
        from_file.mapped_strategy_type == FileTransferStrategyTypes.Shutil
        and to_file.mapped_strategy_type != FileTransferStrategyTypes.HTTP
    ):
        return _strategy_type_map[to_file.mapped_strategy_type]
    elif to_file.mapped_strategy_type == FileTransferStrategyTypes.Shutil:
        return _strategy_type_map[from_file.mapped_strategy_type]
    else:
        raise AttributeError("FileTransfer requires a file transfer strategy to be specified")


class FileTransfer:
    """
    FileTransfer object class that takes two File objects or filepaths (from, to) and a File Transfer Strategy to perform remote or local file transfer operations.

    Attributes:
        from_file: Filepath or File object corresponding to the source file.
        to_file: Filepath or File object corresponding to the destination file.
        order: Order (enum) to execute the file transfer before (Order.BEFORE) or after (Order.AFTER) electron execution.
        strategy: Optional File Transfer Strategy to perform file operations - default will be resolved from provided file schemes.
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
        else:
            self.strategy = _guess_transfer_strategy(from_file, to_file)()

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
        file_transfer_call_dep = None
        return_value_type = FtCallDepReturnValue.FROM_TO

        # local -> local or remote -> remote
        if (not self.from_file.is_remote and not self.to_file.is_remote) or (
            self.from_file.is_remote and self.to_file.is_remote
        ):
            file_transfer_call_dep = self.strategy.cp(self.from_file, self.to_file)
        # local -> remote
        if not self.from_file.is_remote and self.to_file.is_remote:
            file_transfer_call_dep = self.strategy.upload(self.from_file, self.to_file)
        # remote -> local
        if self.from_file.is_remote and not self.to_file.is_remote:
            file_transfer_call_dep = self.strategy.download(self.from_file, self.to_file)

        pre_transfer_hook_call_dep = self.strategy.pre_transfer_hook(
            self.from_file, self.to_file, return_value_type=return_value_type
        )

        return (pre_transfer_hook_call_dep, file_transfer_call_dep)


# Factories


def TransferFromRemote(
    from_filepath: str,
    to_filepath: Union[str, None] = None,
    strategy: Optional[FileTransferStrategy] = None,
    order: Order = Order.BEFORE,
) -> FileTransfer:
    """
    Factory for creating a FileTransfer instance where from_filepath is implicitly created as a remote File Object, and the order (Order.BEFORE) is set so that this file transfer will occur prior to electron execution.

    Args:
        from_filepath: File path corresponding to remote file (source).
        to_filepath: File path corresponding to local file (destination)
        strategy: Optional File Transfer Strategy to perform file operations - default will be resolved from provided file schemes.
        order: Order (enum) to execute the file transfer before (Order.BEFORE) or after (Order.AFTER) electron execution - default is BEFORE

    Returns:
        FileTransfer instance with implicit Order.BEFORE enum set and from (source) file marked as remote
    """
    # override is_remote for the case where from_filepath is of a file:// scheme where the file is remote (rsync ssh)
    is_dir = from_filepath.endswith("/")
    from_file = File(from_filepath, is_remote=True, is_dir=is_dir)
    if is_dir and not to_filepath.endswith("/"):
        raise ValueError("Please specify a directory path (ending with '/') as the destination.")
    to_file = File(to_filepath, is_dir=is_dir)
    return FileTransfer(
        from_file=from_file, to_file=to_file, order=Order.BEFORE, strategy=strategy
    )


def TransferToRemote(
    to_filepath: str,
    from_filepath: Union[str, None] = None,
    strategy: Optional[FileTransferStrategy] = None,
    order: Order = Order.AFTER,
) -> FileTransfer:
    """
    Factory for creating a FileTransfer instance where to_filepath is implicitly created as a remote File Object, and the order (Order.AFTER) is set so that this file transfer will occur post electron execution.

    Args:
        to_filepath: File path corresponding to remote file (destination)
        from_filepath: File path corresponding to local file (source).
        strategy: Optional File Transfer Strategy to perform file operations - default will be resolved from provided file schemes.
        order: Order (enum) to execute the file transfer before (Order.BEFORE) or after (Order.AFTER) electron execution - default is AFTER

    Returns:
        FileTransfer instance with implicit Order.AFTER enum set and to (destination) file marked as remote
    """
    # override is_remote for the case where to_filepath is of a file:// scheme where the file is remote (rsync ssh)
    is_dir = from_filepath and from_filepath.endswith("/")
    from_file = File(from_filepath, is_dir=is_dir)
    if is_dir and not to_filepath.endswith("/"):
        raise ValueError("Please specify a directory path (ending with '/') as the destination.")
    to_file = File(to_filepath, is_remote=True, is_dir=is_dir)

    return FileTransfer(from_file=from_file, to_file=to_file, order=Order.AFTER, strategy=strategy)
