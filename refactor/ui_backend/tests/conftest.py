import pytest
from fastapi_socketio import SocketManager
from main import app
from starlette.testclient import TestClient


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    SocketManager(app=client)
    yield client
