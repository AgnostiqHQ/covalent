from sqlite3 import DatabaseError, OperationalError

import pytest


def test_liveness_endpoint(test_app):
    response = test_app.get("/healthz")
    assert response.status_code == 200


@pytest.mark.parametrize(
    "db_failed_start",
    [(False), (True)],
)
def test_readiness_endpoint(test_app, monkeypatch, db_failed_start):
    def db_mock_init(self):
        if db_failed_start:
            raise DatabaseError()
        else:
            return None

    monkeypatch.setattr("app.core.db.Database.__init__", db_mock_init)
    response = test_app.get("/readyz")
    if not db_failed_start:
        assert response.status_code == 200
    else:
        assert response.status_code == 503
