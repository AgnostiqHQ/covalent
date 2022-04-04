import pytest
from main import app
from starlette.testclient import TestClient


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client
