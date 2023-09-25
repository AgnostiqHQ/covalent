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
from covalent._file_transfer.strategies.blob_strategy import Blob

MOCK_LOCAL_FILEPATH = "/Users/user/data.csv"
MOCK_BLOB_STORAGE_ACCOUNT_URL = "mock-storage-acct.blob.core.windows.net"
MOCK_BLOB_CONTAINER = "mock-container"
MOCK_BLOB_NAME = "covalent-tmp/data.csv"
MOCK_REMOTE_FILEPATH = (
    f"https://{MOCK_BLOB_STORAGE_ACCOUNT_URL}/{MOCK_BLOB_CONTAINER}/{MOCK_BLOB_NAME}"
)
MOCK_CLIENT_ID = "mock-client-id"
MOCK_CLIENT_SECRET = "mock-secret"
MOCK_TENANT_ID = "mock-tenant-id"


@pytest.fixture
def blob_strategy():
    return Blob(MOCK_CLIENT_ID, MOCK_CLIENT_SECRET, MOCK_TENANT_ID)


def test_init(mocker, blob_strategy):
    assert blob_strategy.credentials == (MOCK_TENANT_ID, MOCK_CLIENT_ID, MOCK_CLIENT_SECRET)


def test_get_blob_client(mocker, blob_strategy):
    azure_mock = MagicMock()
    azure_identity_mock = MagicMock()
    azure_storage_blob_mock = MagicMock()

    sys.modules["azure"] = azure_mock
    sys.modules["azure.identity"] = azure_identity_mock
    sys.modules["azure.storage.blob"] = azure_storage_blob_mock

    credential_mock = azure_identity_mock.ClientSecretCredential
    credential_mock.return_value = MagicMock()

    blob_service_client_mock = azure_storage_blob_mock.BlobServiceClient
    blob_service_client_mock.return_value = MagicMock()

    response = blob_strategy._get_blob_service_client(MOCK_BLOB_STORAGE_ACCOUNT_URL)
    assert response == blob_service_client_mock.return_value

    credential_mock.assert_called_once_with(*blob_strategy.credentials)
    blob_service_client_mock.assert_called_once_with(
        account_url=MOCK_BLOB_STORAGE_ACCOUNT_URL, credential=credential_mock.return_value
    )

    sys.modules["azure.storage.blob"] = None
    with pytest.raises(ImportError):
        blob_strategy._get_blob_service_client(MOCK_BLOB_STORAGE_ACCOUNT_URL)

    sys.modules["azure.identity"] = None
    with pytest.raises(ImportError):
        blob_strategy._get_blob_service_client(MOCK_BLOB_STORAGE_ACCOUNT_URL)


def test_parse_blob_uri(blob_strategy):
    result = blob_strategy._parse_blob_uri(MOCK_REMOTE_FILEPATH)

    assert result[0] == MOCK_BLOB_STORAGE_ACCOUNT_URL
    assert result[1] == MOCK_BLOB_CONTAINER
    assert result[2] == MOCK_BLOB_NAME


def test_download_file(mocker, blob_strategy):
    container_client_mock = MagicMock()

    blob_client_mock = container_client_mock.get_blob_client
    blob_client_mock.return_value = MagicMock()

    download_mock = blob_client_mock().download_blob
    stream_mock = MagicMock()
    download_mock.return_value = stream_mock

    readall_mock = stream_mock.readall
    readall_mock().return_value = MagicMock()

    open_mock = mocker.patch("covalent._file_transfer.strategies.blob_strategy.open", mock_open())

    blob_strategy._download_file(container_client_mock, MOCK_BLOB_NAME, MOCK_LOCAL_FILEPATH)

    blob_client_mock.assert_called_with(blob=MOCK_BLOB_NAME)
    open_mock.assert_called_once_with(MOCK_LOCAL_FILEPATH, "wb")
    open_mock().write.assert_called_once_with(readall_mock.return_value)
    download_mock.assert_called_once()


def test_download(mocker, blob_strategy):
    from_file = File(MOCK_REMOTE_FILEPATH)
    to_file = File(MOCK_LOCAL_FILEPATH)

    mocker.patch("covalent._file_transfer.strategies.blob_strategy.app_log")

    blob_service_client_mock = MagicMock()
    mocker.patch(
        "covalent._file_transfer.strategies.blob_strategy.Blob._get_blob_service_client",
        blob_service_client_mock,
    )
    container_client_mock = blob_service_client_mock().get_container_client
    container_client_mock.return_value = MagicMock()

    mkdir_mock = mocker.patch("pathlib.Path.mkdir")

    download_file_mock = MagicMock()
    mocker.patch(
        "covalent._file_transfer.strategies.blob_strategy.Blob._download_file", download_file_mock
    )

    blob_strategy.download(from_file, to_file)()

    blob_service_client_mock.assert_called_with(MOCK_BLOB_STORAGE_ACCOUNT_URL)
    container_client_mock.assert_called_with(MOCK_BLOB_CONTAINER)
    mkdir_mock.assert_any_call(parents=True, exist_ok=True)
    download_file_mock.assert_any_call(
        container_client_mock.return_value, MOCK_BLOB_NAME, Path(MOCK_LOCAL_FILEPATH)
    )


def test_upload_file(mocker, blob_strategy):
    container_client_mock = MagicMock()
    open_mock = mocker.patch("covalent._file_transfer.strategies.blob_strategy.open", mock_open())
    upload_mock = container_client_mock.upload_blob

    blob_strategy._upload_file(container_client_mock, MOCK_LOCAL_FILEPATH, MOCK_BLOB_NAME)

    open_mock.assert_called_once_with(MOCK_LOCAL_FILEPATH, "rb")
    upload_mock.assert_called_once_with(name=MOCK_BLOB_NAME, data=open_mock(), overwrite=True)


def test_upload(mocker, blob_strategy):
    from_file = File(MOCK_LOCAL_FILEPATH)
    to_file = File(MOCK_REMOTE_FILEPATH)

    mocker.patch("covalent._file_transfer.strategies.blob_strategy.app_log")

    blob_service_client_mock = MagicMock()
    mocker.patch(
        "covalent._file_transfer.strategies.blob_strategy.Blob._get_blob_service_client",
        blob_service_client_mock,
    )
    container_client_mock = blob_service_client_mock().get_container_client
    container_client_mock.return_value = MagicMock()

    upload_file_mock = MagicMock()
    mocker.patch(
        "covalent._file_transfer.strategies.blob_strategy.Blob._upload_file", upload_file_mock
    )

    blob_strategy.upload(from_file, to_file)()

    blob_service_client_mock.assert_called_with(MOCK_BLOB_STORAGE_ACCOUNT_URL)
    container_client_mock.assert_called_with(MOCK_BLOB_CONTAINER)
    upload_file_mock.assert_any_call(
        container_client_mock.return_value, MOCK_LOCAL_FILEPATH, Path(MOCK_BLOB_NAME)
    )
