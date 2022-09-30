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

from typing import Optional

from .file import File


class Folder(File):
    """
    Folder class to store components of provided URI including scheme (s3://, file://, ect.), determine if the file is remote,
    and act as facade to facilitate filesystem operations. Folder is a child of the File class which sets `is_dir` flag to True.

    Attributes:
        include_folder: Flag that determines if the folder should be included in the file transfer, if False only contents of folder are transfered.
    """

    def __init__(
        self,
        filepath: Optional[str] = None,
        is_remote: bool = False,
        is_dir: bool = True,
        include_folder: bool = False,
    ):
        super().__init__(filepath, is_remote, is_dir, include_folder)
