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

import json
from pathlib import Path
from typing import Callable

from .. import File
from .transfer_strategy_base import FileTransferStrategy


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

    def _parse_uri(self, gcloud_uri: str):
        raise NotImplementedError

    def _download_file(self, client, source_path: str, destination_path: str) -> None:
        raise NotImplementedError

    def download(self, from_file: File, to_file: File = File()) -> Callable:
        raise NotImplementedError

    def _upload_file(self, client, source_path: str, destination_path: Path) -> None:
        raise NotImplementedError

    def upload(self, from_file: File, to_file: File = File()) -> Callable:
        raise NotImplementedError

    def cp(self, from_file: File, to_file: File = File()) -> File:  # pragma: no cover
        raise NotImplementedError
