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

from covalent_dispatcher._triggers_app.app import available_triggers, get_threadpool, init_trigger


def test_get_threadpool(mocker):
    thread_pool_mocker = mocker.patch("covalent_dispatcher._triggers_app.app.ThreadPoolExecutor")

    first_threadpool = get_threadpool()
    second_threadpool = get_threadpool()

    # Check that it's the same threadpool object
    thread_pool_mocker.assert_called_once()
    assert first_threadpool == second_threadpool


def test_init_trigger(mocker: mock):
    # TODO: Still fixing

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
    init_signature_mock = mocker.patch("covalent_dispatcher._triggers_app.app.signature")
    init_signature_mock.parameters.get.side_effect = {"constructor_param_1": None}.get

    setattr_mock = mocker.patch("covalent_dispatcher._triggers_app.app.setattr")

    init_trigger(trigger_dict)

    init_signature_mock.assert_called_once()
    # assert init_signature_mock.parameters.get.call_count == 3
    # assert len(trigger_dict) == 2
    # tr_class_mock.assert_called_with({"constructor_param_1": "param_1"})
    # assert setattr_mock.call_count == 2


@pytest.mark.parametrize("disable_triggers", [True, False])
def test_register_and_observe(mocker, disable_triggers):
    pass


@pytest.mark.parametrize("disable_triggers", [True, False])
def test_stop_observe(mocker, disable_triggers):
    pass
