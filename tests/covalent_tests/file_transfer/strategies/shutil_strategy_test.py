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


import pytest

from covalent._file_transfer import File
from covalent._file_transfer.strategies.shutil_strategy import Shutil


class TestShutilStrategy:
    MOCK_FROM_FILEPATH = "/home/user/data.csv"
    MOCK_TO_FILEPATH = "/home/user/data.csv.bak"

    def test_cp(self, mocker):
        mocker.patch("os.makedirs")
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
