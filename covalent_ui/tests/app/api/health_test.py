import pytest


def test_liveness_endpoint(test_app):
    response = test_app.get("/healthz")
    assert response.status_code == 200


@pytest.mark.parametrize(
    "path_exists",
    [(False), (True)],
)
def test_readiness_endpoint(test_app, mocker, path_exists):
    mocker.patch("os.path.isdir", return_value=path_exists)
    response = test_app.get("/readyz")
    if path_exists:
        assert response.status_code == 200
    else:
        assert response.status_code == 503
