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
        def callable():
            shutil.copyfile(from_file.filepath, to_file.filepath)

        return callable

    # Local file operations only
    def upload(self, from_file: File, to_file: File = File()) -> File:
        raise NotImplementedError

    # Local file operations only
    def download(self, from_file: File, to_file: File) -> File:
        raise NotImplementedError
