import os

import mock
import nats
import requests
from app.core.config import settings
from app.core.queuer import Queuer


class TestQueuer:

    MOCK_MQ_CONNECTION_URI = "nats_mock:4222"

    @mock.patch.object(nats, "connect", autospec=True)
    def test_get_client(self, mocked_nats, monkeypatch):
        monkeypatch.setattr(settings, "MQ_CONNECTION_URI", self.MOCK_MQ_CONNECTION_URI)
        queuer = Queuer()
        queuer.get_client()
        args, kwargs = mocked_nats.call_args
        (connection_str,) = args
        assert connection_str == self.MOCK_MQ_CONNECTION_URI
