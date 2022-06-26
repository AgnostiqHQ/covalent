import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

from furl import furl

from .enums import FileSchemes

if TYPE_CHECKING:
    from covalent._file_transfer.strategies.rsync_strategy import Rsync


class File:
    def __init__(self, uri: str) -> None:
        if isinstance(uri, str):
            pass
        else:
            raise AttributeError(
                "Only strings are valid filepaths for a covalent.File constructor."
            )

        self.uri_components = furl(uri)
        self.scheme = File.resolve_scheme(uri)
        self.filepath = File.get_file_path(uri)
        self.id = str(uuid.uuid4())

    @property
    def is_directory(self):
        return self.filepath.isdir

    @staticmethod
    def get_file_path(path: str) -> Path:
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
            raise ValueError("No file transfer strategy attached to file")
        else:
            return self.file_transfer_strategy.download(self)
