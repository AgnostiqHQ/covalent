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
