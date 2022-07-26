from abc import ABC, abstractmethod
from pathlib import Path

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

    def pre_transfer_hook(self, from_file: File, to_file: File) -> None:
        # Create any necessary temp files needed for file transfer operations
        from_filepath = from_file.filepath
        to_filepath = to_file.filepath
        is_from_temp_file = from_file.is_temp_file
        is_to_temp_file = to_file.is_temp_file

        def hook():
            if is_from_temp_file:
                from_path_obj = Path(from_filepath)
                from_path_obj.mkdir(parents=True, exist_ok=True)
                from_path_obj.touch()
            if is_to_temp_file:
                to_path_obj = Path(to_filepath)
                to_path_obj.mkdir(parents=True, exist_ok=True)
                to_path_obj.touch()

        return hook
