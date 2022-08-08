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

from abc import ABC
from pathlib import Path
from typing import BinaryIO, Generator, List, Union


class StorageBackend(ABC):
    def __init__(self):
        pass

    def get(self, bucket_name: str, object_name: str) -> Union[Generator[bytes, None, None], None]:
        raise NotImplementedError

    def put(
        self,
        data: BinaryIO,
        bucket_name: str,
        object_name: str,
        length: int,
        metadata: dict = None,
        overwrite: bool = False,
    ) -> (str, str):
        raise NotImplementedError

    def delete(self, bucket_name: str, object_names: List[str]):
        raise NotImplementedError
