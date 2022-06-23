from pathlib import Path

from enums import FileSchemes
from furl import furl


class File:
    def __init__(self, uri: str) -> None:
        if isinstance(uri, str):
            pass
        else:
            raise AttributeError(
                "Only strings are valid filepaths as constructor args to a covalent File object."
            )

        self.uri_components = furl(uri)
        self.scheme = File.resolve_scheme(uri)
        self.filepath = File.get_file_path(uri)

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
