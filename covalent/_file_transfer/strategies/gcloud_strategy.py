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

import json
from pathlib import Path
from typing import Callable, Tuple

from furl import furl

from ..._shared_files import logger
from .. import File
from .transfer_strategy_base import FileTransferStrategy

app_log = logger.app_log


class GCloud(FileTransferStrategy):
    """Implements FileTransferStrategy class to transfer files to/from Google Cloud Storage.

    Args:
        credentials: Path to OAuth 2.0 credentials JSON file for a service account
        project_id: ID of a project in GCP

    Attributes:
        credentials: String containing OAuth 2.0 credentials
        project_id: ID of a project in GCP
    """

    def __init__(self, credentials: str = None, project_id: str = None):
        if credentials is not None:
            credentials_json = Path(credentials).resolve()

            if not credentials_json.is_file():
                raise ValueError("Cloud not locate credentials for GCloud file transfers.")

            with open(credentials_json) as f:
                self.credentials = json.load(f)
        else:
            self.credentials = None

        self.project_id = project_id

    def _get_service_client(self, bucket_name: str):
        """Returns the service client object for the Blob storage account.

        Args:
            bucket_name: Name of a storage bucket in Google Cloud

        Returns:
            Storage client object for the Google Cloud storage service
        """

        try:
            from google.cloud import storage
            from google.oauth2 import service_account
        except ImportError:
            print("Missing required dependency. Reinstall package as `pip install covalent[gcp]`.")
            raise

        return storage.Client(
            project=self.project_id,
            credentials=service_account.Credentials.from_service_account_info(self.credentials),
        ).bucket(bucket_name)

    def _parse_uri(self, gcloud_uri: str) -> Tuple[str, str]:
        """Parses a GCloud object URI and returns the bucket name and the object path.

        Args:
            blob_uri: A URI for an Azure Blob object in the form https://<storage_account_name>.blob.core.windows.net/<container_name>/<blob_name>

        Returns:
            parsed_uri: A tuple containing the storage account name, container name, and blob name
        """

        object_furl = furl(gcloud_uri)

        bucket_name = object_furl.host
        object_path = object_furl.path

        if str(object_path).startswith("/"):
            object_path = Path(str(object_path)[1:])

        return (bucket_name, object_path)

    def _download_file(self, blob_client, destination_path: str) -> None:
        blob_client.download_to_filename(destination_path)

    def download(self, from_file: File, to_file: File = File()) -> Callable:
        from_filepath = from_file.filepath
        to_filepath = to_file.filepath

        bucket_name, object_path = self._parse_uri(from_file.uri)

        app_log.debug(
            f"GCloud download; bucket name: {bucket_name}, from_filepath: {from_filepath}, to_filepath {to_filepath}."
        )

        def callable():
            """Download file or directory from a Google Cloud Storage bucket."""
            from pathlib import Path

            service_client = self._get_service_client(bucket_name)

            blobs = service_client.list_blobs(prefix=object_path)
            for blob in blobs:
                if blob.name.endswith("/"):
                    continue

                dest_obj_path = (
                    Path(to_filepath) / Path(blob.name).relative_to(object_path)
                    if to_file.is_dir
                    else Path(to_filepath)
                )
                dest_obj_path.parent.mkdir(parents=True, exist_ok=True)
                self._download_file(blob, str(dest_obj_path))

        return callable

    def _upload_file(self, service_client, source_path: str, destination_path: Path) -> None:
        blob = service_client.blob(destination_path)
        blob.upload_from_filename(source_path)

    def upload(self, from_file: File, to_file: File = File()) -> Callable:
        from_filepath = from_file.filepath
        to_filepath = to_file.filepath

        bucket_name, object_path = self._parse_uri(to_file.uri)

        app_log.debug(
            f"GCloud upload; bucket name: {bucket_name}, from_filepath: {from_filepath}, to_filepath {to_filepath}."
        )

        def callable():
            """Upload file or directory to a Google Cloud Storage bucket."""
            from pathlib import Path

            service_client = self._get_service_client(bucket_name)

            files = (
                [path for path in Path(from_filepath).rglob("*") if path.is_file()]
                if from_file.is_dir
                else [from_filepath]
            )
            for file in files:
                dest_obj_path = (
                    Path(object_path) / Path(file).relative_to(from_filepath)
                    if to_file.is_dir
                    else Path(object_path)
                )
                self._upload_file(service_client, file, str(dest_obj_path))

        return callable

    def cp(self, from_file: File, to_file: File = File()) -> File:  # pragma: no cover
        raise NotImplementedError
