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
from unittest.mock import MagicMock

import pytest
from furl import furl

from covalent._file_transfer import File
from covalent._file_transfer.strategies.blob_strategy import Blob

MOCK_LOCAL_FILEPATH = "/Users/user/data.csv"
MOCK_BLOB_STORAGE_ACCOUNT_URL = "mock-storage-acct.blob.core.windows.net"
MOCK_BLOB_CONTAINER = "mock-container"
MOCK_REMOTE_FILEPATH = f"https://{MOCK_BLOB_STORAGE_ACCOUNT_URL}/{MOCK_BLOB_CONTAINER}/covalent-tmp/data.csv"
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
    blob_service_client_mock.assert_called_once_with(account_url=MOCK_BLOB_STORAGE_ACCOUNT_URL, credential=credential_mock.return_value)
