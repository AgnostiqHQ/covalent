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

import shutil
from abc import ABC
from pathlib import Path
from typing import BinaryIO, Generator, List, Union

from minio import Minio

from .storagebackend import StorageBackend


class MinioStorageBackend(ABC):
    """Thin wrapper for Minio client

    Attributes:
        client: Minio client instance
        bucket_name: current working bucket name (default: "default")
    """

    def __init__(self, client):
        self.bucket_name = "default"
        self.client = client

    def get(self, bucket_name: str, object_name: str) -> Union[Generator[bytes, None, None], None]:
        """Get object from storage.

        Args:
            bucket_name: name of the bucket
            object_name: name of the object

        Returns:
            A generator yielding a byte stream or None if an
            error occurred in retrieving the object

        """

        try:
            resp = self.client.get_object(bucket_name, object_name)
        except Exception as e:
            # TODO: better logging
            print("Exception in MinioStorageBackend:")
            print(e)
            return None

        if resp.status == 200:
            return resp.stream()
        else:
            return None

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
            metadata: an optional dict of metadata to upload

        Returns:
            (bucket_name, object_name) if write succeeds and ("", "") otherwise

        """

        try:
            res = self.client.put_object(bucket_name, object_name, data, length, metadata=metadata)
        except Exception as e:
            # TODO: better logging
            print("Exception in MinioStorageBackend:")
            print(e)
            res = None

        if res:
            return (bucket_name, object_name)
        else:
            return ("", "")

    def delete(self, bucket_name: str, object_names: List[str]):
        raise NotImplementedError
