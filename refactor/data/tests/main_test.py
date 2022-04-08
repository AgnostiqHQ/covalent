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

from app.core.localstoragebackend import LocalStorageBackend

DIRNAME = os.path.dirname(__file__)
FILENAME = os.path.join(DIRNAME, "./_test_assets/result")


def test_upload_endpoint(test_app, monkeypatch):
    mock_object_name = "mockresult"

    def mock_put(_, data, bucket_name, object_name, length, metadata=None, overwrite=False):
        return (bucket_name, object_name)

    monkeypatch.setattr("app.core.localstoragebackend.LocalStorageBackend.put", mock_put)

    with open(FILENAME, "rb") as f:
        response = test_app.post(
            "/api/v0/fs/upload",
            files=[("file", (mock_object_name, f, "application/octet-stream"))],
        )
        d = response.json()
        assert d["filename"] == mock_object_name
        assert d["path"] == "default"


def test_download_endpoint(test_app, monkeypatch):
    mock_object_name = "mockresult"

    def mock_file_reader(filename):
        with open(filename, "rb") as f:
            yield from f

    def mock_get(_, bucket_name, object_name):
        return mock_file_reader(FILENAME)

    monkeypatch.setattr("app.core.localstoragebackend.LocalStorageBackend.get", mock_get)

    response = test_app.get("/api/v0/fs/download", params={"file_location": FILENAME}, stream=True)
    assert response.status_code < 400
    assert len(response.content) > 0
