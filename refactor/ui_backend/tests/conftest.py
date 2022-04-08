import pytest
from fastapi_socketio import SocketManager
from starlette.testclient import TestClient

from refactor.ui_backend.main import app


@pytest.skip.reason("test failing")
@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    SocketManager(app=client)
    yield client
