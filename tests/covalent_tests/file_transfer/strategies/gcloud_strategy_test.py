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

import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open

import pytest

from covalent._file_transfer.strategies.gcloud_strategy import GCloud

MOCK_LOCAL_FILEPATH = "/Users/user/data.csv"
MOCK_STORAGE_BUCKET = "mock-bucket"
MOCK_REMOTE_OBJECT_NAME = "/covalent-tmp/data.csv"
MOCK_REMOTE_FILEPATH = f"gs://{MOCK_STORAGE_BUCKET}{MOCK_REMOTE_OBJECT_NAME}"
MOCK_CREDENTIALS_PATH = "/path/to/mock/credentials"
MOCK_PROJECT_ID = "mock-project-id"
MOCK_CREDENTIALS = {
    "mock-key": "mock-value",
}


@pytest.fixture
def gcloud_strategy():
    strategy = GCloud()
    strategy.credentials = MOCK_CREDENTIALS
    strategy.project_id = MOCK_PROJECT_ID

    return strategy


def test_init(mocker):
    mocker.patch("pathlib.Path.is_file", return_value=True)
    open_mock = mocker.patch(
        "covalent._file_transfer.strategies.gcloud_strategy.open", mock_open()
    )
    json_load_mock = mocker.patch("json.load", return_value=MOCK_CREDENTIALS)

    strategy = GCloud(MOCK_CREDENTIALS_PATH, MOCK_PROJECT_ID)

    open_mock.assert_called_once_with(Path(MOCK_CREDENTIALS_PATH).resolve())
    json_load_mock.assert_called_once_with(open_mock())

    assert strategy.credentials == MOCK_CREDENTIALS
    assert strategy.project_id == MOCK_PROJECT_ID

    strategy = GCloud()

    assert strategy.credentials is None
    assert strategy.project_id is None

    mocker.patch("pathlib.Path.is_file", return_value=False)
    with pytest.raises(ValueError):
        strategy = GCloud(MOCK_CREDENTIALS_PATH, MOCK_PROJECT_ID)


def test_get_service_client(mocker, gcloud_strategy):
    sys.modules["google"] = MagicMock()
    cloud_mock = MagicMock()
    sys.modules["google.cloud"] = cloud_mock
    oauth2_mock = MagicMock()
    sys.modules["google.oauth2"] = oauth2_mock

    storage_client_mock = cloud_mock.storage.Client
    service_account_mock = oauth2_mock.service_account.Credentials.from_service_account_info
    bucket_mock = storage_client_mock().bucket

    client = gcloud_strategy._get_service_client(MOCK_STORAGE_BUCKET)

    service_account_mock.assert_called_once_with(MOCK_CREDENTIALS)
    storage_client_mock.assert_called_with(
        project=MOCK_PROJECT_ID, credentials=service_account_mock.return_value
    )
    bucket_mock.assert_called_once_with(MOCK_STORAGE_BUCKET)

    assert client == bucket_mock.return_value

    sys.modules["google.oauth2"] = None
    with pytest.raises(ImportError):
        gcloud_strategy._get_service_client(MOCK_STORAGE_BUCKET)

    sys.modules["google.cloud"] = None
    with pytest.raises(ImportError):
        gcloud_strategy._get_service_client(MOCK_STORAGE_BUCKET)


def test_parse_uri(gcloud_strategy):
    result = gcloud_strategy._parse_uri(MOCK_REMOTE_FILEPATH)

    assert result[0] == MOCK_STORAGE_BUCKET
    assert result[1] == MOCK_REMOTE_OBJECT_NAME
