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

import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open

import pytest

from covalent._file_transfer import File
from covalent._file_transfer.strategies.gcloud_strategy import GCloud

MOCK_LOCAL_FILEPATH = "/Users/user/data.csv"
MOCK_STORAGE_BUCKET = "mock-bucket"
MOCK_REMOTE_OBJECT_NAME = "covalent-tmp/data.csv"
MOCK_REMOTE_FILEPATH = f"gs://{MOCK_STORAGE_BUCKET}/{MOCK_REMOTE_OBJECT_NAME}"
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
    assert str(result[1]) == MOCK_REMOTE_OBJECT_NAME


def test_download_file(gcloud_strategy):
    blob_client_mock = MagicMock()
    destination_path = MOCK_LOCAL_FILEPATH
    download_mock = blob_client_mock.download_to_filename

    gcloud_strategy._download_file(blob_client_mock, destination_path)

    download_mock.assert_called_once_with(destination_path)


def test_download(mocker, gcloud_strategy):
    from_file = File(MOCK_REMOTE_FILEPATH)
    to_file = File(MOCK_LOCAL_FILEPATH)

    mocker.patch("covalent._file_transfer.strategies.gcloud_strategy.app_log")

    parse_uri_mock = mocker.patch(
        "covalent._file_transfer.strategies.gcloud_strategy.GCloud._parse_uri"
    )
    parse_uri_mock.return_value = (MOCK_STORAGE_BUCKET, MOCK_REMOTE_OBJECT_NAME)

    get_service_client_mock = mocker.patch(
        "covalent._file_transfer.strategies.gcloud_strategy.GCloud._get_service_client"
    )
    list_blobs_mock = get_service_client_mock().list_blobs
    blob_mock = MagicMock()
    list_blobs_mock.return_value = [blob_mock]
    blob_mock.name = MOCK_REMOTE_OBJECT_NAME

    mkdir_mock = mocker.patch("pathlib.Path.mkdir")
    download_file_mock = mocker.patch(
        "covalent._file_transfer.strategies.gcloud_strategy.GCloud._download_file"
    )

    gcloud_strategy.download(from_file, to_file)()

    parse_uri_mock.assert_called_once_with(MOCK_REMOTE_FILEPATH)
    get_service_client_mock.assert_called_with(MOCK_STORAGE_BUCKET)
    list_blobs_mock.assert_called_once_with(prefix=MOCK_REMOTE_OBJECT_NAME)
    mkdir_mock.assert_called_once_with(parents=True, exist_ok=True)
    download_file_mock.assert_called_once_with(blob_mock, MOCK_LOCAL_FILEPATH)


def test_upload_file(gcloud_strategy):
    service_client = MagicMock()
    source_path = MOCK_LOCAL_FILEPATH
    destination_path = MOCK_REMOTE_OBJECT_NAME

    blob_mock = service_client.blob
    upload_mock = blob_mock().upload_from_filename

    gcloud_strategy._upload_file(service_client, source_path, destination_path)

    blob_mock.assert_called_with(destination_path)
    upload_mock.assert_called_once_with(source_path)


def test_upload(mocker, gcloud_strategy):
    from_file = File(MOCK_LOCAL_FILEPATH)
    to_file = File(MOCK_REMOTE_FILEPATH)

    parse_uri_mock = mocker.patch(
        "covalent._file_transfer.strategies.gcloud_strategy.GCloud._parse_uri"
    )
    parse_uri_mock.return_value = (MOCK_STORAGE_BUCKET, MOCK_REMOTE_OBJECT_NAME)

    mocker.patch("covalent._file_transfer.strategies.gcloud_strategy.app_log")
    get_service_client_mock = mocker.patch(
        "covalent._file_transfer.strategies.gcloud_strategy.GCloud._get_service_client"
    )
    upload_file_mock = mocker.patch(
        "covalent._file_transfer.strategies.gcloud_strategy.GCloud._upload_file"
    )

    gcloud_strategy.upload(from_file, to_file)()

    parse_uri_mock.assert_called_once_with(MOCK_REMOTE_FILEPATH)
    get_service_client_mock.assert_called_with(MOCK_STORAGE_BUCKET)
    upload_file_mock.assert_called_once_with(
        get_service_client_mock.return_value, MOCK_LOCAL_FILEPATH, MOCK_REMOTE_OBJECT_NAME
    )
