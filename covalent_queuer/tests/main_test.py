import base64
import os

import pytest
from app.core.queue import Queue

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "./_test_assets/result")


@pytest.mark.skip(reason="Needs updating")
def test_submit_endpoint(test_app, monkeypatch):
    MOCK_DISPATCH_ID = "1234"

    async def mock_publish(_, topic, payload):
        assert payload["dispatch_id"] == MOCK_DISPATCH_ID

    async def mock_create_result(_, result_base64_encoded):
        return {"dispatch_id": MOCK_DISPATCH_ID}

    monkeypatch.setattr("app.core.queue.Queuer.publish", mock_publish)
    monkeypatch.setattr("app.core.api.DataService.create_result", mock_create_result)

    with open(filename, "rb") as f:
        files = {"result_pkl_file": f}
        response = test_app.post("/api/v0/submit/dispatch", files=files)
        assert response.status_code == 202
