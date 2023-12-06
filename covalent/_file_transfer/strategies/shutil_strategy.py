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

import os
import shutil

from .. import File
from .transfer_strategy_base import FileTransferStrategy


class Shutil(FileTransferStrategy):
    """
    Implements Base FileTransferStrategy class to copy files locally

    The copying is done in-process using shutil.copyfile.
    """

    def __init__(
        self,
    ):
        pass

    # return callable to copy files in the local file system
    def cp(self, from_file: File, to_file: File = File()) -> None:
        """
        Get a callable that copies a file from one location to another locally

        Args:
            from_file: File to copy from
            to_file: File to copy to. Defaults to File().

        Returns:
            A callable that copies a file from one location to another locally
        """

        def callable():
            os.makedirs(os.path.dirname(to_file.filepath), exist_ok=True)
            shutil.copyfile(from_file.filepath, to_file.filepath)

        return callable

    # Local file operations only
    def upload(self, from_file: File, to_file: File = File()) -> File:
        raise NotImplementedError

    # Local file operations only
    def download(self, from_file: File, to_file: File) -> File:
        raise NotImplementedError
