import base64
import os

from app.core.localstoragebackend import LocalStorageBackend

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "./_test_assets/result")


def test_upload_endpoint(test_app, monkeypatch):
    MOCK_OBJECT_NAME = "mockresult"

    def mock_put(_, data, bucket_name, object_name, length, metadata=None):
        return (bucket_name, object_name)

    monkeypatch.setattr("app.core.localstoragebackend.LocalStorageBackend.put", mock_put)

    with open(filename, "rb") as f:
        response = test_app.post(
            "/api/v0/fs/upload",
            files=[("file", (MOCK_OBJECT_NAME, f, "application/octet-stream"))],
        )
        d = response.json()
        assert d["filename"] == MOCK_OBJECT_NAME
        assert d["path"] == "default"
