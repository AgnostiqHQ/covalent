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

from unittest import mock

import pytest

from covalent.triggers import BaseTrigger


def test_register(mocker):
    """
    Testing whether the trigger is able
    to register itself to the Triggers server
    """

    mock_config = "mock-config"
    mock_json_data = {"trigger_server_addr": "mock-json-data", "name": "mock-name"}
    mocker.patch("covalent.triggers.base.get_config", return_value=mock_config)
    mocker.patch("covalent.triggers.base.BaseTrigger.to_dict", return_value=mock_json_data)
    requests_mock = mocker.patch("covalent.triggers.base.requests")

    base_trigger = BaseTrigger()
    base_trigger.register()

    requests_mock.post.assert_called_once_with(
        f"http://{mock_config}:{mock_config}/api/triggers/register",
        json=mock_json_data,
    )


@pytest.mark.parametrize(
    "use_internal_func, mock_status",
    [
        (True, {"status": "mocked-status"}),
        (False, {"status": "mocked-status"}),
    ],
)
def test_get_status(mocker, use_internal_func, mock_status):
    """
    Testing whether get_status internally gets called with
    the right arguments in different conditions
    """

    base_trigger = BaseTrigger()
    base_trigger.use_internal_funcs = use_internal_func

    if use_internal_func:
        mock_bulk_get_res = mock.Mock()
        mock_bulk_get_res.dispatches = [mock.Mock()]
        mock_bulk_get_res.dispatches[0].status = mock_status["status"]
        mocker.patch(
            "covalent_dispatcher._service.app.get_dispatches_bulk", return_value=mock_bulk_get_res
        )

        status = base_trigger._get_status()

    else:
        mock_get_status = mocker.patch("covalent.get_result", return_value=mock_status)
        status = base_trigger._get_status()
        mock_get_status.assert_called_once()

    assert status == "mocked-status"


@pytest.mark.parametrize("use_internal_func", [True, False])
@pytest.mark.parametrize("is_pending", [True, False])
def test_do_redispatch(mocker, use_internal_func, is_pending):
    """
    Testing whether the trigger's internal do_redispatch function
    with the right arguments in different conditions
    """

    mock_redispatch_id = "test_dispatch_id"
    mock_wrapper = mock.MagicMock(return_value=mock_redispatch_id)
    mock_redispatch = mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.redispatch", return_value=mock_wrapper
    )
    mock_start = mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.start", return_value=mock_redispatch_id
    )

    base_trigger = BaseTrigger()
    base_trigger.use_internal_funcs = use_internal_func

    redispatch_id = base_trigger._do_redispatch(is_pending)

    if is_pending:
        mock_start.assert_called_once()
        mock_wrapper.assert_not_called()
    else:
        mock_redispatch.assert_called()

    assert redispatch_id == mock_redispatch_id


@pytest.mark.parametrize("lattice_dispatch_id", [None, "mock_id"])
@pytest.mark.parametrize("mock_status", [None, "some_status"])
def test_trigger(mocker, lattice_dispatch_id, mock_status):
    """
    Testing whether the trigger's internal trigger function
    with the right arguments in different conditions
    """

    base_trigger = BaseTrigger()
    base_trigger.lattice_dispatch_id = lattice_dispatch_id

    if not lattice_dispatch_id:
        err_str = "`lattice_dispatch_id` is None. Please attach this trigger to a lattice before triggering."
        with pytest.raises(RuntimeError) as re:
            base_trigger.trigger()
            assert re.match(err_str)

    else:
        mock_redispatch_id = "test_redispatch_id"

        mock_get_status = mocker.patch(
            "covalent.triggers.base.BaseTrigger._get_status", return_value=mock_status
        )
        mock_do_redispatch = mocker.patch(
            "covalent.triggers.base.BaseTrigger._do_redispatch", return_value=mock_redispatch_id
        )

        base_trigger.trigger()

        mock_get_status.assert_called_once()

        if mock_status is None:
            mock_do_redispatch.assert_called_with(True)
        else:
            mock_do_redispatch.assert_called_once()
            assert mock_redispatch_id in base_trigger.new_dispatch_ids
