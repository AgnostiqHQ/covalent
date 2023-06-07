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


import pytest

from covalent._file_transfer import File
from covalent._file_transfer.strategies.shutil_strategy import Shutil


class TestShutilStrategy:
    MOCK_FROM_FILEPATH = "/home/user/data.csv"
    MOCK_TO_FILEPATH = "/home/user/data.csv.bak"

    def test_cp(self, mocker):
        mock_copyfile = mocker.patch("shutil.copyfile")
        from_file = File(TestShutilStrategy.MOCK_FROM_FILEPATH)
        to_file = File(TestShutilStrategy.MOCK_TO_FILEPATH)
        Shutil().cp(from_file, to_file)()
        mock_copyfile.assert_called_with(from_file.filepath, to_file.filepath)

    def test_download_failure(self, mocker):
        from_file = File(TestShutilStrategy.MOCK_FROM_FILEPATH)
        to_file = File(TestShutilStrategy.MOCK_TO_FILEPATH)

        with pytest.raises(NotImplementedError):
            Shutil().download(from_file, to_file)

    def test_upload_failure(self, mocker):
        from_file = File(TestShutilStrategy.MOCK_FROM_FILEPATH)
        to_file = File(TestShutilStrategy.MOCK_TO_FILEPATH)

        with pytest.raises(NotImplementedError):
            Shutil().upload(from_file, to_file)
