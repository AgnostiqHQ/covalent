import pytest
from main import app
from starlette.testclient import TestClient
from fastapi_socketio import SocketManager


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    SocketManager(app=client)
    yield client
