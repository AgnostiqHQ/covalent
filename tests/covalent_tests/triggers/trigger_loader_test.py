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


from unittest import mock

import pytest

from covalent.triggers import BaseTrigger, DirTrigger, TimeTrigger
from covalent.triggers.trigger_loader import TriggerLoader


@pytest.fixture
def trigger_loader():
    return TriggerLoader()


def test_trigger_loader_init(trigger_loader):
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


def test_trigger_loader_get_and_set(mocker, trigger_loader):
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
