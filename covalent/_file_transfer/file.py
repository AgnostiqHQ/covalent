# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

import uuid
from pathlib import Path
from typing import Optional

from furl import furl

from .enums import FileSchemes, FileTransferStrategyTypes, SchemeToStrategyMap


class File:
    """
    File class to store components of provided URI including scheme (s3://, file://, ect.) determine if the file is remote,
    and acts a facade to facilitate filesystem operations.

    Attributes:
        filepath: File path corresponding to the file.
        is_remote: Flag determining if file is remote (override). Default is resolved automatically from file scheme.
        is_dir: Flag determining if file is a directory (override). Default is determined if file uri contains trailing slash.
        include_folder: Flag that determines if the folder should be included in the file transfer, if False only contents of folder are transfered.
    """

    _is_remote = False
    _is_dir = False
    _include_folder = False

    def __init__(
        self,
        filepath: Optional[str] = None,
        is_remote: bool = False,
        is_dir: bool = False,
        include_folder: bool = False,
    ):
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
            self._is_remote = True

        if is_dir:
            self._is_dir = True

        if include_folder:
            self._include_folder = True

        self.scheme = File.resolve_scheme(filepath)
        self._path_object = File.get_path_obj(filepath)
        self.uri = File.get_uri(self.scheme, filepath)

    @property
    def is_temp_file(self):
        return self.filepath == self.get_temp_filepath()

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

    @property
    def filepath(self) -> str:
        path_obj = self._path_object
        if not self._include_folder and self.is_dir:
            path_obj = path_obj / "/"
        path_obj.normalize()
        filepath = str(path_obj)
        if self._include_folder:
            filepath = filepath.rstrip("/")
        return filepath

    @property
    def is_dir(self):
        return self._is_dir or self._path_object.isdir

    def touch(self):
        Path(self.filepath).touch()

    @staticmethod
    def get_path_obj(path: str):
        path_components = furl(path)
        path_components.scheme = None
        path_components.path.normalize()
        return path_components.path

    @staticmethod
    def get_uri(scheme: str, path: str) -> str:
        path_components = furl(path)
        path_components.scheme = scheme
        path_components.path.normalize()
        return path_components.url

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
