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

from ..._shared_files import logger
from .. import File
from .transfer_strategy_base import FileTransferStrategy

app_log = logger.app_log


class Blob(FileTransferStrategy):
    """
    Implements FileTransferStrategy class to transfer files to/from Azure Blob Storage.
    """

    def __init__(
        self, 
        storage_account_name: str = None, 
        storage_account_domain: str = "blob.core.windows.net",
        storage_container_name: str = None,
        client_id: str = None,
        client_secret: str = None,
        tenant_id: str = None,
    ):
        self.storage_account_url = f"https://{storage_account_name}.{storage_account_domain}/"
        self.storage_container_name = storage_container_name
        self.credentials = (tenant_id, client_id, client_secret)

    def _get_blob_service_client(self):
        try:
            from azure.identity import ClientSecretCredential
            from azure.storage.blob import BlobServiceClient
        except ImportError:
            print("Missing required dependency. Reinstall package as `pip install covalent[azure]`.")
            raise
            
        return BlobServiceClient(account_url=self.storage_account_url, credential=ClientSecretCredential(*self.credentials))

    def download(self, from_file: File, to_file: File = File()) -> File:
        """Download files or the contents of folders from Azure Blob Storage."""
    
        from_filepath = from_file.filepath
        to_filepath = to_file.filepath

        if from_filepath.startswith("/"):
            from_filepath = from_filepath[1:]

        app_log.debug(
            f"Blob download; storage account: {self.storage_account_url}, from_filepath: {from_filepath}, to_filepath {to_filepath}."
        )
        

        if from_file._is_dir:
            def callable():
                """Download directory from a storage container in Azure blob storage account."""
                from pathlib import Path

                blob_service_client = self._get_blob_service_client()
                container_client = blob_service_client.get_container_client(self.storage_container_name)

                blobs = container_client.list_blobs(name_starts_with=from_filepath)
                for blob in blobs:
                    dest_obj_path = Path(to_filepath) / Path(blob.name).relative_to(from_filepath)
                    dest_obj_path.parent.mkdir(parents=True, exist_ok=True)
                    blob_client = container_client.get_blob_client(blob=blob.name)

                    with open(dest_obj_path, mode="wb") as f:
                        stream = blob_client.download_blob()
                        f.write(stream.readall())
                
        else:
            def callable():
                """Download file from a storage container in Azure blob storage account."""

                blob_service_client = self._get_blob_service_client()
                blob_client = blob_service_client.get_blob_client(container=self.storage_container_name, blob=from_filepath)

                with open(to_filepath, mode="wb") as f:
                    stream = blob_client.download_blob()
                    f.write(stream.readall())

        return callable
    
    def upload(self, from_file: File, to_file: File = File()) -> File:
        """Upload files or the contents of folders to Azure Blob Storage."""

        from_filepath = from_file.filepath
        to_filepath = to_file.filepath

        if to_filepath.startswith("/"):
            to_filepath = to_filepath.strip("/")

        if from_file._is_dir:
            def callable():
                """Upload directory to a storage container in Azure blob storage account."""
                from pathlib import Path

                blob_service_client = self._get_blob_service_client()
                container_client = blob_service_client.get_container_client(self.storage_container_name)

                files = [path for path in Path(from_filepath).rglob("*") if path.is_file()]
                for file in files:
                    dest_obj_path = Path(to_filepath) / Path(file).relative_to(from_filepath)

                    with open(file, mode="rb") as f:
                        container_client.upload_blob(name=str(dest_obj_path), data=f, overwrite=True)

        else:
            def callable():
                """Upload a file to a storage container in Azure blob storage account."""

                blob_service_client = self._get_blob_service_client()
                container_client = blob_service_client.get_container_client(self.storage_container_name)

                with open(from_filepath, mode="rb") as f:
                    container_client.upload_blob(name=to_filepath, data=f, overwrite=True)

        return callable
    
    def cp(self, from_file: File, to_file: File = File()) -> File:
        raise NotImplementedError
