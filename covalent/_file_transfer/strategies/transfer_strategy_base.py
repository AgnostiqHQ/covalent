from abc import ABC, abstractmethod
from pathlib import Path

from ..enums import FtCallDepReturnValue
from ..file import File


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

    def pre_transfer_hook(
        self,
        from_file: File,
        to_file: File,
        return_value_type: FtCallDepReturnValue = FtCallDepReturnValue.FROM_TO,
    ) -> None:
        # Create any necessary temp files needed for file transfer operations
        from_filepath = from_file.filepath
        to_filepath = to_file.filepath
        is_from_temp_file = from_file.is_temp_file
        is_to_temp_file = to_file.is_temp_file

        # return value to be injected into kwargs of electron decorated fn as 'files'
        if return_value_type == FtCallDepReturnValue.TO:
            return_value = to_filepath
        elif return_value_type == FtCallDepReturnValue.FROM:
            return_value = from_filepath
        else:
            return_value = (from_filepath, to_filepath)

        def hook():
            if is_from_temp_file:
                from_path_obj = Path(from_filepath)
                from_path_obj.parent.mkdir(parents=True, exist_ok=True)
                from_path_obj.touch()
            if is_to_temp_file:
                to_path_obj = Path(to_filepath)
                to_path_obj.parent.mkdir(parents=True, exist_ok=True)
                to_path_obj.touch()
            return return_value

        return hook
