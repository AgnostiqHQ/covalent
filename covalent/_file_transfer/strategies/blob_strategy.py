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

import os
from furl import furl
from typing import Callable, Tuple

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
            print("Missing required dependency. Reinstall package as `pip install covalent[azure]`.")
            raise

        return BlobServiceClient(account_url=storage_account_url, credential=ClientSecretCredential(*self.credentials))

    def _parse_blob_uri(self, blob_uri: str) -> Tuple[str, str, str]:
        """

        """

        blob_furl = furl(blob_uri)

        storage_account_url = blob_furl.host
        blob_path = blob_furl.path

        storage_container_name = blob_path.segments[0]
        base_path = "/".join(blob_path.segments[1:])

    def _download_file(container_client, blob_name: str, destination_path: str):
        blob_client = container_client.get_blob_client(blob=blob_name)

        with open(destination_path, "wb") as f:
            stream = blob_client.download_blob()
            f.write(stream.readall())

    def download(self, from_file: File, to_file: File = File()) -> Callable:
        """Download files or the contents of folders from Azure Blob Storage."""

        from_filepath = from_file.filepath
        to_filepath = to_file.filepath

        storage_account_url, storage_container_name, base_path = self._parse_blob_uri(from_file.uri)

        app_log.debug(
            f"Blob download; storage account: {self.storage_account_url}, from_filepath: {from_filepath}, to_filepath {to_filepath}."
        )

        def callable():
            """Download file or directory from an Azure Blob storage container."""
            from pathlib import Path

            blob_service_client = self._get_blob_service_client(storage_account_url)
            container_client = blob_service_client.get_container_client(storage_container_name)

            blobs = container_client.list_blobs(name_starts_with=base_path) if from_file.is_dir else [base_path]
            for blob in blobs:
                blob_name = blob.name if from_file.is_dir else base_path
                dest_obj_path = Path(to_filepath) / Path(blob.name).relative_to(base_path) if to_file.is_dir else to_filepath
                dest_obj_path.parent.mkdir(parents=True, exist_ok=True)
                self._download_file(container_client, blob_name, dest_obj_path)

        return callable

    def upload(self, from_file: File, to_file: File = File()) -> Callable:
        """Upload files or the contents of folders to Azure Blob Storage."""

        from_filepath = from_file.filepath
        to_filepath = to_file.filepath

        storage_account_url, storage_container_name, base_path = self._parse_blob_uri(to_file.uri)

        if from_file._is_dir:
            def callable():
                """Upload directory to a storage container in Azure blob storage account."""
                from pathlib import Path

                blob_service_client = self._get_blob_service_client(storage_account_url)
                container_client = blob_service_client.get_container_client(storage_container_name)

                files = [path for path in Path(from_filepath).rglob("*") if path.is_file()]
                for file in files:
                    dest_obj_path = Path(base_path) / Path(file).relative_to(from_filepath)

                    with open(file, mode="rb") as f:
                        container_client.upload_blob(name=str(dest_obj_path), data=f, overwrite=True)

        else:
            def callable():
                """Upload a file to a storage container in Azure blob storage account."""

                blob_service_client = self._get_blob_service_client(storage_account_url)
                container_client = blob_service_client.get_container_client(storage_container_name)

                with open(from_filepath, mode="rb") as f:
                    container_client.upload_blob(name=to_filepath, data=f, overwrite=True)

        return callable

    def cp(self, from_file: File, to_file: File = File()) -> File:
        raise NotImplementedError
