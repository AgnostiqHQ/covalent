from fastapi.testclient import TestClient

from covalent_ui.app import fastapi_app


def test_overview():
    client = TestClient(fastapi_app)
    response = client.get("/api/v1/dispatches/overview")
    assert response.status_code in [200]
