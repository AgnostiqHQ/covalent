import pytest


def test_liveness_endpoint(test_app):
    response = test_app.get("/healthz")
    assert response.status_code == 200
