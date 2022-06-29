from abc import ABC, abstractmethod

from covalent._file_transfer.file import File


class FileTransferStrategy(ABC):
    @abstractmethod
    def move(self, from_file: File, to_file: File) -> None:
        raise NotImplementedError

    # download here implies 'from' is a remote source
    @abstractmethod
    def download(self, from_file: File, to_file: File) -> File:
        raise NotImplementedError

    # upload here implies 'to' is a remote source
    @abstractmethod
    def upload(self, from_file: File, to_file: File) -> None:
        raise NotImplementedError
