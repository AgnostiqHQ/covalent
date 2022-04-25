import asyncio

import pytest


def test_liveness_endpoint(test_app):
    response = test_app.get("/healthz")
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "nats_timeout",
    [(False), (True)],
)
def test_readiness_endpoint(test_app, mocker, monkeypatch, nats_timeout):

    # simulate nats timeout
    async def queuer_mock(_):
        wait_time = 200 if nats_timeout else 0
        await asyncio.sleep(wait_time)
        return None

    monkeypatch.setattr("app.core.queuer.Queuer.get_client", queuer_mock)
    response = test_app.get("/readyz")
    if not nats_timeout:
        assert response.status_code == 200
    else:
        assert response.status_code == 503
