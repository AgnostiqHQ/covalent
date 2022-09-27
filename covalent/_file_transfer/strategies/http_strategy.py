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
