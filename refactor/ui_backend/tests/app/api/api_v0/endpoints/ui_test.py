import asyncio
import os
from time import sleep
from unittest.mock import MagicMock, Mock

import pytest
from aiolimiter import AsyncLimiter
from app.api.api_v0.endpoints.ui import dispatch_set, throttle_request_update_notify
from fastapi import BackgroundTasks


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


MOCK_DISPATCH_ID = 'e7829'
MOCK_TASK_ID = 123

@pytest.mark.asyncio
async def test_throttle_request_update(test_app, mocker, monkeypatch):

    socketio_obj_mock = AsyncMock()
    limiter_one_per_second = AsyncLimiter(1,2) # enforce throttle of 1 call every 2 seconds

    monkeypatch.setattr("app.api.api_v0.endpoints.ui.limiter",limiter_one_per_second)
    monkeypatch.setattr(test_app,"sio",socketio_obj_mock)

    tasks = []

    # should only call on edges 1st and last time as all calls within 2 second window
    # and deduping calls with same dispatch, task id pairs
    for i in range(0,25):
        tasks.append(asyncio.create_task(throttle_request_update_notify(test_app, MOCK_DISPATCH_ID, MOCK_TASK_ID)))

    await asyncio.gather(*tasks)
    assert socketio_obj_mock.emit.call_count == 2



def test_ui_update_endpoint(test_app, mocker):



    spy = mocker.spy(BackgroundTasks, "add_task")

    response = test_app.put(f"/api/v0/ui/workflow/{MOCK_DISPATCH_ID}/task/{MOCK_TASK_ID}",)
    assert response.status_code == 200

    spy.assert_called_with(
        mocker.ANY, # self
        throttle_request_update_notify, # add_to_bucket
        mocker.ANY, # app
        MOCK_DISPATCH_ID,
        MOCK_TASK_ID
    )

@pytest.mark.asyncio
async def test_draft_endpoint(test_app, mocker, monkeypatch):

    #socketio_obj_mock = AsyncMock()
    #monkeypatch.setattr(test_app,"sio",socketio_obj_mock)
    notify_frontend = mocker.patch("app.api.api_v0.endpoints.ui.notify_frontend")

    REQUEST_BODY = {
        "payload": {}
    }

    response = test_app.post(f"/api/v0/ui/workflow/draft", json=REQUEST_BODY)
    assert response.status_code == 200

    notify_frontend.assert_called_with(mocker.ANY,"draw-request",REQUEST_BODY)
