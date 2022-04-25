def test_liveness_endpoint(test_app):
    response = test_app.get("/healthz")
    assert response.status_code == 200


def test_readiness_endpoint(test_app):
    response = test_app.get("/readyz")
    assert response.status_code == 200
