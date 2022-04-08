import os

import mock
import nats
import requests
from app.core.queuer import Queuer


class TestQueuer:

    MOCK_MQ_CONNECTION_URI = "NATS:4222"

    @mock.patch.object(nats, "connect", autospec=True)
    @mock.patch.dict(os.environ, {"MQ_CONNECTION_URI": MOCK_MQ_CONNECTION_URI})
    def test_get_client(self, mocked_nats):
        queuer = Queuer()
        queuer.get_client()
        mocked_nats.assert_called_once_with(self.MOCK_MQ_CONNECTION_URI)
