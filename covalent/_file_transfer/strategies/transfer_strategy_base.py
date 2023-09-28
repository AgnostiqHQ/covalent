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

from abc import ABC, abstractmethod
from pathlib import Path

from ..enums import FtCallDepReturnValue
from ..file import File


class FileTransferStrategy(ABC):
    """
    Base FileTransferStrategy class that defines the interface for file transfer strategies exposing common methods for performing copy, download, and upload operations.

    """

    # move file (from) source (to) destination
    @abstractmethod
    def cp(self, from_file: File, to_file: File) -> None:
        raise NotImplementedError

    # download here implies 'from' is a remote source
    @abstractmethod
    def download(self, from_file: File, to_file: File) -> File:
        raise NotImplementedError

    # upload here implies 'to' is a remote source
    @abstractmethod
    def upload(self, from_file: File, to_file: File) -> None:
        raise NotImplementedError

    def pre_transfer_hook(
        self,
        from_file: File,
        to_file: File,
        return_value_type: FtCallDepReturnValue = FtCallDepReturnValue.FROM_TO,
    ) -> None:
        # Create any necessary temp files needed for file transfer operations
        from_filepath = from_file.filepath
        to_filepath = to_file.filepath
        is_from_temp_file = from_file.is_temp_file
        is_to_temp_file = to_file.is_temp_file

        # return value to be injected into kwargs of electron decorated fn as 'files'
        if return_value_type == FtCallDepReturnValue.TO:
            return_value = to_filepath
        elif return_value_type == FtCallDepReturnValue.FROM:
            return_value = from_filepath
        else:
            return_value = (from_filepath, to_filepath)

        def hook():
            if is_from_temp_file:
                from_path_obj = Path(from_filepath)
                from_path_obj.parent.mkdir(parents=True, exist_ok=True)
                from_path_obj.touch()
            if is_to_temp_file:
                to_path_obj = Path(to_filepath)
                to_path_obj.parent.mkdir(parents=True, exist_ok=True)
                to_path_obj.touch()
            return return_value

        return hook
