import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

from furl import furl

from covalent._file_transfer.enums import FileSchemes

if TYPE_CHECKING:
    from covalent._file_transfer.strategies.rsync_strategy import Rsync


class File:
    def __init__(self, local_path: str = "", remote_path: str = "") -> None:
        if not isinstance(local_path, str) or not isinstance(remote_path, str):
            raise AttributeError(
                "Only strings are valid filepaths for a covalent File constructor."
            )

        self.id = str(uuid.uuid4())
        self.scheme = File.resolve_scheme(local_path)
        self.local_filepath = File.get_filepath(local_path)
        self.remote_filepath = File.get_filepath(remote_path)

        if not self.remote_filepath:
            self.remote_filepath = self.get_temp_filepath()
        if not self.local_filepath:
            self.local_filepath = self.get_temp_filepath()

    def get_temp_filepath(self):
        return f"/tmp/{self.id}"

    @staticmethod
    def is_directory(path):
        return File.get_filepath(path).isdir

    @staticmethod
    def get_filepath(path: str) -> str:
        path_components = furl(path)
        path_components.scheme = None
        return path_components.path

    @staticmethod
    def resolve_scheme(path: str) -> str:
        scheme = furl(path).scheme
        if scheme == FileSchemes.Globus:
            return FileSchemes.Globus
        if scheme == FileSchemes.S3:
            return FileSchemes.S3
        if scheme is None or scheme == FileSchemes.File:
            return FileSchemes.File
        raise ValueError(f"Provided File scheme ({scheme}) is not supported.")

    def attach_strategy(self, file_transfer_strategy: "Rsync"):
        self.file_transfer_strategy = file_transfer_strategy

    def download(self):
        if not self.file_transfer_strategy:
            # TODO raise more accurate error
            raise ValueError("No file transfer strategy attached to file to perform download.")
        else:
            return self.file_transfer_strategy.download(self)

    def upload(self):
        if not self.file_transfer_strategy:
            # TODO raise more accurate error
            raise ValueError("No file transfer strategy attached to file to perform upload")
        else:
            return self.file_transfer_strategy.upload(self)
