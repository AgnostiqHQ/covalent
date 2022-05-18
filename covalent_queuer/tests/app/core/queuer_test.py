import os

import mock
import nats
import pytest
import requests
from app.core.queue import Queue


@pytest.mark.parametrize(
    reason="No longer supporting the NATS message queue. This test needs to be updated."
)
class TestQueue:

    MOCK_MQ_CONNECTION_URI = "localhost:4222"

    @mock.patch.object(nats, "connect", autospec=True)
    @mock.patch.dict(os.environ, {"MQ_CONNECTION_URI": MOCK_MQ_CONNECTION_URI})
    def test_get_client(self, mocked_nats):
        queue = Queue()
        queue.get_client()
        mocked_nats.assert_called_once_with(self.MOCK_MQ_CONNECTION_URI)
