import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

from furl import furl

from covalent._file_transfer.enums import (
    FileSchemes,
    FileTransferStrategyTypes,
    SchemeToStrategyMap,
)

if TYPE_CHECKING:
    from covalent._file_transfer.strategies.rsync_strategy import Rsync


class File:
    def __init__(self, filepath: str = None, is_remote=False) -> None:
        if not isinstance(filepath, str) or filepath is not None:
            raise AttributeError(
                "Only strings are valid filepaths for a covalent File constructor."
            )

        # assign default filepath of form /tmp/{id}
        if filepath is None:
            filepath = self.get_temp_filepath()

        # override is_remote boolean
        if is_remote:
            self._is_remote = is_remote

        self.id = str(uuid.uuid4())
        self.scheme = File.resolve_scheme(filepath)
        self.filepath = File.get_filepath(filepath)

    def get_temp_filepath(self):
        return f"/tmp/{self.id}"

    @property
    def is_remote(self):
        return self._is_remote or self.scheme in [
            FileSchemes.S3,
            FileSchemes.Globus,
            FileSchemes.HTTP,
            FileSchemes.HTTPS,
        ]

    @property
    def mapped_strategy_type(self) -> FileTransferStrategyTypes:
        return SchemeToStrategyMap[str(self.scheme)]

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
