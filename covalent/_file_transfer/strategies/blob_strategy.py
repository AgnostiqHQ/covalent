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

from pathlib import Path
from typing import Callable, Tuple

from furl import furl

from ..._shared_files import logger
from .. import File
from .transfer_strategy_base import FileTransferStrategy

app_log = logger.app_log


class Blob(FileTransferStrategy):
    """Implements FileTransferStrategy class to transfer files to/from Azure Blob Storage.

    Args:
        client_id: ID of a service principal authorized to perform the transfer
        client_secret: Corresponding secret key for the service principal credentials
        tenant_id: The Azure Active Directory tenant ID which owns the cloud resources.

    Attributes:
        credentials: A tuple containing (client_id, client_secret, tenant_id)
    """

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        tenant_id: str = None,
    ):
        self.credentials = (tenant_id, client_id, client_secret)

    def _get_blob_service_client(self, storage_account_url):
        """Returns the service client object for the Blob storage account.

        Args:
            storage_account_url: Fully qualified URL of the storage account, e.g., https://account_name.blob.core.windows.net

        Returns:
            blob_service_client: A client object for the Azure Blob service
        """

        try:
            from azure.identity import ClientSecretCredential
            from azure.storage.blob import BlobServiceClient
        except ImportError:
            print(
                "Missing required dependency. Reinstall package as `pip install covalent[azure]`."
            )
            raise

        return BlobServiceClient(
            account_url=storage_account_url, credential=ClientSecretCredential(*self.credentials)
        )

    def _parse_blob_uri(self, blob_uri: str) -> Tuple[str, str, str]:
        """Parses a blob URI and returns the account name, container name, and blob name.

        Args:
            blob_uri: A URI for an Azure Blob object in the form https://<storage_account_name>.blob.core.windows.net/<container_name>/<blob_name>

        Returns:
            parsed_uri: A tuple containing the storage account name, container name, and blob name
        """

        blob_furl = furl(blob_uri)

        storage_account_url = blob_furl.host
        blob_path = blob_furl.path

        storage_container_name = blob_path.segments[0]
        base_path = "/".join(blob_path.segments[1:])

        return (storage_account_url, storage_container_name, base_path)

    def _download_file(self, container_client, blob_name: str, destination_path: Path) -> None:
        """Downloads a single blob to the local filesystem.

        Args:
            container_client: Azure Blob storage container client object
            blob_name: Name of the blob object within the scope of the container
            destination_path: Path on the local filesystem where the file will be saved
        """

        blob_client = container_client.get_blob_client(blob=blob_name)

        with open(destination_path, "wb") as f:
            stream = blob_client.download_blob()
            f.write(stream.readall())

    def download(self, from_file: File, to_file: File = File()) -> Callable:
        """Download files or the contents of folders from Azure Blob Storage.

        Args:
            from_file: File object referencing an object in Azure Blob storage
            to_file: File object referencing a path in the local filesystem

        Returns:
            callable: Download function that is injected into wrapper_fn
        """

        from_filepath = from_file.filepath
        to_filepath = to_file.filepath

        storage_account_url, storage_container_name, base_path = self._parse_blob_uri(
            from_file.uri
        )

        app_log.debug(
            f"Blob download; storage account: {storage_account_url}, from_filepath: {from_filepath}, to_filepath {to_filepath}."
        )

        def callable():
            """Download file or directory from an Azure Blob storage container."""
            from pathlib import Path

            blob_service_client = self._get_blob_service_client(storage_account_url)
            container_client = blob_service_client.get_container_client(storage_container_name)

            blobs = (
                container_client.list_blobs(name_starts_with=base_path)
                if from_file.is_dir
                else [base_path]
            )
            for blob in blobs:
                blob_name = blob.name if from_file.is_dir else base_path
                dest_obj_path = (
                    Path(to_filepath) / Path(blob.name).relative_to(base_path)
                    if to_file.is_dir
                    else Path(to_filepath)
                )
                dest_obj_path.parent.mkdir(parents=True, exist_ok=True)
                self._download_file(container_client, blob_name, dest_obj_path)

        return callable

    def _upload_file(self, container_client, file_path: str, dest_obj_path: Path) -> None:
        """Uploads a single file to Azure Blob storage.

        Args:
            container_client: Azure Blob storage container client object
            file_path: Path on the local filesystem to a file that is uploaded
            dest_obj_path: Path in a blob storage container where the file will be saved
        """

        with open(file_path, "rb") as f:
            container_client.upload_blob(name=str(dest_obj_path), data=f, overwrite=True)

    def upload(self, from_file: File, to_file: File = File()) -> Callable:
        """Upload files or the contents of folders to Azure Blob Storage.

        Args:
            from_file: File object referencing a path in the local filesystem
            to_file: File object referencing an object in Azure Blob storage

        Returns:
            callable: Upload function that is injected into wrapper_fn
        """

        from_filepath = from_file.filepath
        to_filepath = to_file.filepath

        storage_account_url, storage_container_name, base_path = self._parse_blob_uri(to_file.uri)

        app_log.debug(
            f"Blob upload; storage account: {storage_account_url}, from_filepath: {from_filepath}, to_filepath {to_filepath}."
        )

        def callable():
            """Upload file or directory to an Azure Blob storage container."""
            from pathlib import Path

            blob_service_client = self._get_blob_service_client(storage_account_url)
            container_client = blob_service_client.get_container_client(storage_container_name)

            files = (
                [path for path in Path(from_filepath).rglob("*") if path.is_file()]
                if from_file.is_dir
                else [from_filepath]
            )
            for file in files:
                dest_obj_path = (
                    Path(base_path) / Path(file).relative_to(from_filepath)
                    if to_file.is_dir
                    else Path(base_path)
                )
                self._upload_file(container_client, file, dest_obj_path)

        return callable

    def cp(self, from_file: File, to_file: File = File()) -> File:  # pragma: no cover
        raise NotImplementedError
