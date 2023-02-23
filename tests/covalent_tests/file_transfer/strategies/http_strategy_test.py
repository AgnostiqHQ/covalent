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
from covalent._file_transfer.strategies.http_strategy import HTTP


class TestHTTPStrategy:
    MOCK_LOCAL_FILEPATH = "/Users/user/data.csv"
    MOCK_REMOTE_FILEPATH = "http://example.com/data.csv"

    def test_download(self, mocker):
        # validate urlretrieve called with appropriate arguments
        urlretrieve_mock = mocker.patch("urllib.request.urlretrieve")
        from_file = File(self.MOCK_REMOTE_FILEPATH)
        to_file = File(self.MOCK_LOCAL_FILEPATH)
        HTTP().download(from_file, to_file)()
        urlretrieve_mock.assert_called_with(from_file.uri, to_file.filepath)

    @pytest.mark.parametrize(
        "operation",
        [
            ("cp"),
            ("upload"),
        ],
    )
    def test_upload_cp_failure(self, operation, mocker):
        with pytest.raises(NotImplementedError):
            if operation == "upload":
                HTTP().upload(File(self.MOCK_REMOTE_FILEPATH), File(self.MOCK_LOCAL_FILEPATH))()
            elif operation == "cp":
                HTTP().cp(File(self.MOCK_REMOTE_FILEPATH), File(self.MOCK_LOCAL_FILEPATH))()
