import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

from furl import furl

from covalent._file_transfer.enums import (
    FileSchemes,
    FileTransferStrategyTypes,
    SchemeToStrategyMap,
)

if TYPE_CHECKING:
    from covalent._file_transfer.strategies.rsync_strategy import Rsync


class File:

    _is_remote = False

    def __init__(self, filepath: Union[str, None] = None, is_remote=False) -> None:
        if not isinstance(filepath, str) and filepath is not None:
            raise AttributeError(
                "Only strings are valid filepaths for a covalent File constructor."
            )

        self.id = str(uuid.uuid4())

        # assign default filepath of form /tmp/{id}
        if filepath is None:
            filepath = self.get_temp_filepath()

        # override is_remote boolean
        if is_remote:
            self._is_remote = is_remote

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
            FileSchemes.FTP,
        ]

    @property
    def mapped_strategy_type(self) -> FileTransferStrategyTypes:
        return SchemeToStrategyMap[self.scheme.value]

    @staticmethod
    def is_directory(path):
        return File.get_filepath(path).isdir

    @staticmethod
    def get_filepath(path: str) -> str:
        path_components = furl(path)
        path_components.scheme = None
        return path_components.path

    @staticmethod
    def resolve_scheme(path: str) -> FileSchemes:
        scheme = furl(path).scheme
        if scheme == FileSchemes.Globus:
            return FileSchemes.Globus
        if scheme == FileSchemes.S3:
            return FileSchemes.S3
        if scheme == FileSchemes.FTP:
            return FileSchemes.FTP
        if scheme == FileSchemes.HTTP:
            return FileSchemes.HTTP
        if scheme == FileSchemes.HTTPS:
            return FileSchemes.HTTPS
        if scheme is None or scheme == FileSchemes.File:
            return FileSchemes.File
        raise ValueError(f"Provided File scheme ({scheme}) is not supported.")
