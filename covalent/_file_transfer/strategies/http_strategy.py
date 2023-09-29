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

import urllib.request

from .. import File
from .transfer_strategy_base import FileTransferStrategy


class HTTP(FileTransferStrategy):
    """
    Implements Base FileTransferStrategy class to use HTTP to download files from public URLs.
    """

    # return callable to download here implies 'from' is a remote source
    def download(self, from_file: File, to_file: File = File()) -> File:
        from_filepath = from_file.uri
        to_filepath = to_file.filepath

        def callable():
            urllib.request.urlretrieve(from_filepath, to_filepath)
            return to_filepath

        return callable

    # HTTP Strategy is read only
    def upload(self, from_file: File, to_file: File = File()) -> File:
        raise NotImplementedError

    # HTTP Strategy is read only
    def cp(self, from_file: File, to_file: File = File()) -> File:
        raise NotImplementedError
