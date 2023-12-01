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
from covalent._file_transfer.strategies.http_strategy import HTTP


class TestHTTPStrategy:
    MOCK_LOCAL_FILEPATH = "/tmp/data.csv"
    MOCK_REMOTE_FILEPATH = "http://example.com/data.csv"

    def test_download(self, mocker):
        # validate urlretrieve called with appropriate arguments
        mock_get = mocker.patch("requests.get")
        from_file = File(self.MOCK_REMOTE_FILEPATH)
        to_file = File(self.MOCK_LOCAL_FILEPATH)
        HTTP().download(from_file, to_file)()
        mock_get.assert_called_with(from_file.uri, stream=True)

    @pytest.mark.parametrize(
        "operation",
        [
            ("cp"),
            ("upload"),
        ],
    )
    def test_upload_failure(self, operation, mocker):
        with pytest.raises(NotImplementedError):
            HTTP().cp(File(self.MOCK_REMOTE_FILEPATH), File(self.MOCK_LOCAL_FILEPATH))()
