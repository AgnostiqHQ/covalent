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

from covalent.triggers import BaseTrigger, DirTrigger, TimeTrigger
from covalent.triggers.trigger_loader import TriggerLoader


@pytest.fixture
def trigger_loader():
    """
    Fixture to return an instance of TriggerLoader for testing purposes
    """

    return TriggerLoader()


def test_trigger_loader_init(trigger_loader):
    """
    Testing whether TriggerLoader is initialized as expected
    with the default available triggers loaded
    """

    expected_keys = [BaseTrigger.__name__, DirTrigger.__name__, TimeTrigger.__name__]

    expected_values = [BaseTrigger, DirTrigger, TimeTrigger]

    assert all(
        expected_keys[i] in trigger_loader.available_triggers.keys()
        for i in range(len(expected_keys))
    )

    assert all(
        expected_values[i] in trigger_loader.available_triggers.values()
        for i in range(len(expected_values))
    )


@pytest.mark.parametrize("attr_is_present", [True, False])
def test_trigger_loader_new(mocker, trigger_loader, attr_is_present):
    """
    Testing whether the same instance of TriggerLoader is returned
    even when called multiple times, instead of creating a new instance
    and reloading everything from scratch
    """

    super_mock = mock.MagicMock()
    mock.patch("covalent.triggers.trigger_loader.super", super_mock)

    mocker.patch("covalent.triggers.trigger_loader.hasattr", return_value=attr_is_present)
    super_mock = mocker.patch(
        "covalent.triggers.trigger_loader.super", return_value=super(TriggerLoader, trigger_loader)
    )

    new_trigger_loader = TriggerLoader()

    if not attr_is_present:
        super_mock.assert_called_once()
        assert new_trigger_loader != trigger_loader
    else:
        assert new_trigger_loader == trigger_loader


def test_trigger_loader_get_and_set(trigger_loader):
    """
    Testing whether the TriggerLoader instance works equivalent
    to a dictionary for setting and getting loaded triggers
    """

    test_dict = {
        "a": 0,
        "b": 1,
        "c": 2,
    }

    trigger_loader.available_triggers = test_dict.copy()

    # Test get:
    expected_val = test_dict["a"]
    actual_val = trigger_loader["a"]

    assert expected_val == actual_val

    # Test set:
    test_k, test_v = "b", 5
    trigger_loader[test_k] = test_v

    assert trigger_loader.available_triggers[test_k] == test_v
