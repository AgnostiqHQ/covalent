from abc import ABC, abstractmethod

from covalent._file_transfer.file import File


class FileTransferStrategy(ABC):
    """
    Base FileTransferStrategy class that defines the interface for file transfer strategies exposing common methods for performing copy, download, and upload operations.

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
