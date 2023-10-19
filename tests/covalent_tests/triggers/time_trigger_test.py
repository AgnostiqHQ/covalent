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

from functools import partial
from unittest import mock

import pytest

from covalent.triggers import TimeTrigger

counter = 0


@pytest.fixture
def time_trigger():
    """
    Fixture to get a sample TimeTrigger instance for testing purposes
    """

    return TimeTrigger(None)


def is_set_side_effect(set_stop):
    """
    Utility function to test Event object sets its
    value in the expected manner
    """

    global counter
    if set_stop or counter == 1:
        return True
    counter += 1
    return False


@pytest.mark.parametrize("set_stop", [False, True])
def test_observe(mocker, time_trigger, set_stop):
    """
    Testing whether the observe method of TimeTrigger
    starts with the right arguments with the right conditions
    """

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
    """
    Testing whether TimeTrigger's stop method
    actually stops the trigger when called
    """

    time_trigger.stop_flag = mock.Mock()

    time_trigger.stop()

    time_trigger.stop_flag.set.assert_called_once()
