# Copyright 2023 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for the Triggers server endpoints"""


from unittest import mock

import pytest
from fastapi import HTTPException

import covalent_dispatcher._triggers_app.app as app
from covalent_dispatcher._triggers_app.app import (
    available_triggers,
    get_threadpool,
    init_trigger,
    register_and_observe,
    stop_observe,
)


class MockSigClass:
    def __init__(self, params) -> None:
        self.parameters = params


@pytest.fixture
def file_to_test():
    """
    Functions of which file will be mocked
    """

    return "covalent_dispatcher._triggers_app.app"


def test_get_threadpool(mocker: mock, file_to_test: str):
    """
    Testing whether the threadpool received from
    get_threadpool is actually the same instance
    even when called multiple times
    """

    thread_pool_mocker = mocker.patch(f"{file_to_test}.ThreadPoolExecutor")

    first_threadpool = get_threadpool()
    second_threadpool = get_threadpool()

    # Check that it's the same threadpool object
    thread_pool_mocker.assert_called_once()
    assert first_threadpool == second_threadpool


def test_init_trigger(mocker: mock, file_to_test: str):
    """
    Testing whether a trigger can be obtained/recreated
    from its dictionary representation on the Triggers server
    """

    tr_class_mock = mock.Mock()
    test_available_triggers = {
        "test_tr_name": tr_class_mock,
    }

    trigger_dict = {
        "name": "test_tr_name",
        "constructor_param_1": "param_1",
        "tr_attribute_1": "attr_2",
        "tr_attribute_2": "attr_3",
    }

    mocker.patch.object(available_triggers, "available_triggers", test_available_triggers)
    init_signature_mock = mocker.patch(
        f"{file_to_test}.signature",
        return_value=MockSigClass({"constructor_param_1": "not_param"}),
    )

    setattr_mock = mocker.patch(f"{file_to_test}.setattr")

    init_trigger(trigger_dict)

    init_signature_mock.assert_called_once()
    tr_class_mock.assert_called_with(**{"constructor_param_1": "param_1"})
    assert setattr_mock.call_count == 2
    assert len(trigger_dict) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("disable_triggers", [True, False])
@pytest.mark.parametrize("use_internal_funcs", [True, False])
@pytest.mark.parametrize("observe_blocks", [True, False])
@pytest.mark.parametrize("contains_triggers", [True, False])
async def test_register_and_observe(
    mocker: mock,
    file_to_test: str,
    disable_triggers: bool,
    use_internal_funcs: bool,
    observe_blocks: bool,
    contains_triggers: bool,
):
    """
    Testing whether registration of the trigger as well as
    starting of its observe method works as expected
    """

    test_request = mock.Mock()
    test_request.json = mock.AsyncMock()
    mocker.patch(f"{file_to_test}.disable_triggers", disable_triggers)

    if disable_triggers:
        with pytest.raises(HTTPException) as http_exc:
            await register_and_observe(test_request)

        assert http_exc.value.status_code == 412
        assert http_exc.value.detail == "Trigger endpoints are disabled as requested"

    else:
        test_dispatch_id = "test_dispatch_id"
        test_active_triggers = {test_dispatch_id: [] if contains_triggers else None}

        trigger_mock = mock.Mock()
        trigger_mock.use_internal_funcs = use_internal_funcs
        trigger_mock.observe_blocks = observe_blocks

        get_threadpool_mock = mocker.patch(f"{file_to_test}.get_threadpool")
        init_trigger_mock = mocker.patch(f"{file_to_test}.init_trigger", return_value=trigger_mock)
        get_running_loop_mock = mocker.patch(f"{file_to_test}.asyncio.get_running_loop")
        active_triggers_mock = mocker.patch.object(app, "active_triggers", test_active_triggers)

        await register_and_observe(test_request)

        get_threadpool_mock.assert_called_once()
        test_request.json.assert_called_once()
        init_trigger_mock.assert_called_once()
        if use_internal_funcs:
            get_running_loop_mock.assert_called_once()
        if observe_blocks:
            get_threadpool_mock.return_value.submit.assert_called_once()
        else:
            trigger_mock.observe.assert_called_once()

        test_active_triggers[test_dispatch_id] = [trigger_mock]
        assert test_active_triggers == active_triggers_mock


@pytest.mark.asyncio
@pytest.mark.parametrize("disable_triggers", [True, False])
async def test_stop_observe(
    mocker: mock,
    file_to_test: str,
    disable_triggers: bool,
):
    """
    Testing whether stopping of the triggers' observe method
    works as expected for all the triggers of all given dispatch ids
    """

    test_dispatch_id = "test_dispatch_id"
    test_request = mock.Mock()
    test_request.json = mock.AsyncMock(return_value=[test_dispatch_id])
    mocker.patch(f"{file_to_test}.disable_triggers", disable_triggers)

    if disable_triggers:
        with pytest.raises(HTTPException) as http_exc:
            await stop_observe(test_request)

        assert http_exc.value.status_code == 412
        assert http_exc.value.detail == "Trigger endpoints are disabled as requested"

    else:
        trigger_mock = mock.Mock()
        test_active_triggers = {test_dispatch_id: [trigger_mock]}
        mocker.patch.object(app, "active_triggers", test_active_triggers)

        await stop_observe(test_request)

        test_request.json.assert_called_once()
        trigger_mock.stop.assert_called_once()
