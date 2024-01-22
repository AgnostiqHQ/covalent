# Copyright 2023 Agnostiq Inc.
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

from covalent._shared_files.qelectron_utils import get_qelectron_db_path


@pytest.mark.parametrize(
    "db_exists",
    [
        True,
        False,
    ],
)
def test_get_qelectron_db_path(mocker, db_exists):
    """Test the get_qelectron_db_path function."""

    mock_database = mocker.patch("covalent.quantum.qserver.database.Database")
    mock_database.return_value.get_db_path.return_value.exists.return_value = db_exists

    dispatch_id = "mock_dispatch_id"
    task_id = 0

    db_path = get_qelectron_db_path(dispatch_id, 0)

    mock_database.return_value.get_db_path.assert_called_once_with(
        dispatch_id=dispatch_id, node_id=task_id
    )
    mock_database.return_value.get_db_path.return_value.exists.assert_called_once()

    if db_exists:
        assert db_path is not None
    else:
        assert db_path is None
