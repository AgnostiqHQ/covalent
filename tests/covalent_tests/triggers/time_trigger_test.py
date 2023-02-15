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

from functools import partial
from unittest import mock

import pytest

from covalent.triggers import TimeTrigger

counter = 0


@pytest.fixture
def time_trigger():
    return TimeTrigger(None)


def is_set_side_effect(set_stop):
    global counter
    if set_stop or counter == 1:
        return True
    counter += 1
    return False


@pytest.mark.parametrize("set_stop", [False, True])
def test_observe(mocker, time_trigger, set_stop):
    test_time_gap = 2

    event_is_set_mock = mocker.patch(
        "covalent.triggers.time_trigger.Event.is_set",
        side_effect=partial(is_set_side_effect, set_stop),
    )
    sleep_mock = mocker.patch("time.sleep")
    trigger_mock = mocker.patch("covalent.triggers.TimeTrigger.trigger")

    time_trigger.time_gap = test_time_gap

    time_trigger.observe()

    if not set_stop:
        event_is_set_mock.call_count == 2
        sleep_mock.assert_called_with(test_time_gap)
        trigger_mock.assert_called_once()
    else:
        event_is_set_mock.assert_called_once()


def test_stop(time_trigger):
    time_trigger.stop_flag = mock.Mock()

    time_trigger.stop()

    time_trigger.stop_flag.set.assert_called_once()
