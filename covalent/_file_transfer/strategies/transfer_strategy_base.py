from abc import ABC, abstractmethod

from covalent._file_transfer.file import File


class FileTransferStrategy(ABC):
    """
    FileTransferStrategy class that outlines a common set of methods that perform operations
    such as moving, uploading and downloading files to local or remote filesystems.

    """

    # move file (from) source (to) destination
    @abstractmethod
    def cp(self, from_file: File, to_file: File) -> None:
        raise NotImplementedError

    # download here implies 'from' is a remote source
    @abstractmethod
    def download(self, from_file: File, to_file: File) -> File:
        raise NotImplementedError

    # upload here implies 'to' is a remote source
    @abstractmethod
    def upload(self, from_file: File, to_file: File) -> None:
        raise NotImplementedError
