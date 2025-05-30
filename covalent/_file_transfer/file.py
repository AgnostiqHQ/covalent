# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid
from pathlib import Path
from typing import Optional

from furl import furl

from .enums import FileSchemes

_is_remote_scheme = {
    FileSchemes.S3.value: True,
    FileSchemes.Blob.value: True,
    FileSchemes.GCloud.value: True,
    FileSchemes.Globus.value: True,
    FileSchemes.HTTP.value: True,
    FileSchemes.HTTPS.value: True,
    FileSchemes.FTP.value: True,
    FileSchemes.File: False,
}


# For registering additional file transfer strategies; this will be called by
# `register_uploader`` and `register_downloader``
def register_remote_scheme(s: str):
    _is_remote_scheme[s] = True


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
        return self._is_remote or _is_remote_scheme[self.scheme]

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
    def resolve_scheme(path: str) -> str:
        scheme = furl(path).scheme
        host = furl(path).host
        # Canonicalize file system paths to file:// urls
        if not scheme:
            return FileSchemes.File.value
        if scheme in _is_remote_scheme:
            return scheme
        else:
            raise ValueError(f"Provided File scheme ({scheme}) is not supported.")
