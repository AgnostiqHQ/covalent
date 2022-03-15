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

import os
import shutil
from abc import ABC
from pathlib import Path
from typing import BinaryIO, Generator, List, Union

from .storagebackend import StorageBackend


def file_reader(filename: str):
    """Construct generator from file"""
    with open(filename, "rb") as f:
        yield from f


class LocalStorageBackend(StorageBackend):
    """Filesystem storage backend.

    Buckets = plain directories and object_names resolve to file
    paths. Custom metadata is not supported.

    Attributes:
        base_dir: root directory in which all buckets will be created
        bucket_name: current working bucket name (default: "default")

    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.bucket_name = "default"

    def get(self, bucket_name: str, object_name: str) -> Union[Generator[bytes, None, None], None]:
        """Get object from storage.

        Args:
            bucket_name: name of the bucket
            object_name: name of the object


        Returns:
            A generator yielding a byte stream
        """

        p = self.base_dir / Path(bucket_name) / Path(object_name)
        if not p.is_file():
            return None
        return file_reader(p)

    def put(
        self,
        data: BinaryIO,
        bucket_name: str,
        object_name: str,
        length: int,
        metadata: dict = None,
    ) -> (str, str):
        """Upload object to storage.

        Args:
            data: a binary file-like object
            bucket_name: name of the bucket
            object_name: name of the destination object
            length: number of bytes to upload
            metadata: not supported

        Returns:
            (bucket_name, object_name) if write succeeds and ("", "") otherwise

        """

        p = self.base_dir / Path(bucket_name) / Path(object_name)
        # Check that bucket name resolves to a subdirectory of base_dir
        # and bucket_name/object_name resolves to under bucket_name.
        try:
            abs_base = str(Path(self.base_dir).resolve(True))
            abs_bucket = str((abs_base / Path(bucket_name)).resolve(True))
        except FileNotFoundError:
            return ("", "")

        abs_p = str(p.resolve())

        if not abs_bucket.startswith(abs_base):
            return ("", "")

        if not abs_p.startswith(abs_bucket):
            return ("", "")

        if not p.parent.is_dir():
            p.parent.mkdir(parents=True)

        tmpdir = self.base_dir / Path(".tmp")
        if not tmpdir.is_dir():
            tmpdir.mkdir()

        tmppath = tmpdir / Path(object_name)

        try:
            # Ensure atomicity by writing to a temp file first and
            # then renaming it.

            with tmppath.open("wb") as tmp:
                shutil.copyfileobj(data, tmp)

            os.replace(tmppath, p)

            return (bucket_name, object_name)
        except:
            return ("", "")
