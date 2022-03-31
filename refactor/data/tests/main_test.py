import base64
import os

from app.core.localstoragebackend import LocalStorageBackend

DIRNAME = os.path.dirname(__file__)
FILENAME = os.path.join(DIRNAME, "./_test_assets/result")


def test_upload_endpoint(test_app, monkeypatch):
    mock_object_name = "mockresult"

    def mock_put(_, data, bucket_name, object_name, length, metadata=None):
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
