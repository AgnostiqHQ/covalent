import os
import base64
from refactor.queuer.app.core.queuer import Queuer

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, './_test_assets/result.pkl')


def test_submit_endpoint(test_app, monkeypatch):
    MOCK_DISPATCH_ID = "1234"

    async def mock_publish(_,topic, payload):
        assert payload["dispatch_id"] == MOCK_DISPATCH_ID

    async def mock_create_result(_,result_base64_encoded):
        return {
            "dispatch_id": MOCK_DISPATCH_ID
        }

    monkeypatch.setattr("refactor.queuer.app.core.queuer.Queuer.publish", mock_publish)
    monkeypatch.setattr("refactor.queuer.app.core.api.DataService.create_result", mock_create_result)

    with open(filename, 'rb') as f:

        # encode binary to base64
        result_binary = f.read()
        result_base64 = base64.b64encode(result_binary).decode('utf-8')

        body = {
            "result_object": result_base64
        }
        response = test_app.post("/api/v0/submit/dispatch", json=body)
        assert response.status_code == 202
