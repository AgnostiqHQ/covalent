# Copyright 2023 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

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
)


class MockSigClass:
    def __init__(self, params) -> None:
        self.parameters = params


@pytest.fixture
def file_to_test():
    return "covalent_dispatcher._triggers_app.app"


def test_get_threadpool(mocker: mock, file_to_test: str):
    thread_pool_mocker = mocker.patch(f"{file_to_test}.ThreadPoolExecutor")

    first_threadpool = get_threadpool()
    second_threadpool = get_threadpool()

    # Check that it's the same threadpool object
    thread_pool_mocker.assert_called_once()
    assert first_threadpool == second_threadpool


def test_init_trigger(mocker: mock, file_to_test: str):
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
    test_request = mock.Mock()
    test_request.json = mock.AsyncMock()
    mocker.patch(f"{file_to_test}.disable_triggers", disable_triggers)

    if disable_triggers:
        with pytest.raises(HTTPException) as http_exc:
            await register_and_observe(test_request)

        assert http_exc.value.status_code == 412
        assert http_exc.value.detail == "Trigger endpoints are disabled as requested"
    else:
        pass
