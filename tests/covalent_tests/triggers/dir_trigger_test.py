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

from covalent.triggers.dir_trigger import DirEventHandler, DirTrigger


@pytest.fixture
def event_to_func_names():
    """
    Event type to function name mappings
    """

    return {
        "test_a": "test_func_a",
        "test_b": "test_func_b",
        "test_c": "test_func_c",
        "test_d": "test_func_d",
        "test_e": "test_func_e",
    }


@pytest.fixture
def dir_trigger(event_to_func_names):
    """
    Fixture to obtain a sample DirTrigger instance for testing
    """

    test_dir_path = "test_dir_path"
    test_event_names = list(event_to_func_names.keys())[:4]
    return DirTrigger(test_dir_path, test_event_names)


def test_event_handler_init():
    """
    Testing whether DirEventHandler initializes as expected
    """

    dir_event_handler = DirEventHandler()
    for k, v in dir_event_handler.supported_event_to_func_names.items():
        assert v == f"on_{k}"


def test_attach_methods_to_handler(mocker, event_to_func_names, dir_trigger):
    """
    Testing whether the correct `on_*` methods are attached to
    the event handler for each event type as given by the user
    """

    event_handler_mock = mock.Mock()
    event_handler_mock.supported_event_to_func_names = event_to_func_names

    mocker.patch("covalent.triggers.DirTrigger.trigger")
    setattr_mock = mocker.patch("covalent.triggers.dir_trigger.setattr")

    dir_trigger.event_handler = event_handler_mock
    dir_trigger.attach_methods_to_handler()

    assert setattr_mock.call_count == len(dir_trigger.event_names)


@pytest.mark.parametrize("test_recursive", [True, False])
def test_observe(mocker, dir_trigger, test_recursive):
    """
    Testing the observe method of DirTrigger
    calls all the necessary functions
    """

    event_loop_mock = mocker.patch("covalent.triggers.dir_trigger.asyncio.get_running_loop")
    event_handler_mock = mocker.patch("covalent.triggers.dir_trigger.DirEventHandler")
    attach_mock = mocker.patch(
        "covalent.triggers.dir_trigger.DirTrigger.attach_methods_to_handler"
    )
    observer_schedule_mock = mocker.patch("covalent.triggers.dir_trigger.Observer.schedule")
    observer_start_mock = mocker.patch("covalent.triggers.dir_trigger.Observer.start")

    dir_trigger.recursive = test_recursive
    dir_trigger.observe()

    event_loop_mock.assert_called_once()
    event_handler_mock.assert_called_once()
    attach_mock.assert_called_once()
    observer_schedule_mock.assert_called_once()
    observer_start_mock.assert_called_once()


def test_stop(dir_trigger):
    """
    Testing stop function of DirTrigger
    stops the background running Observer
    """

    observer_mock = mock.Mock()

    dir_trigger.observer = observer_mock
    dir_trigger.stop()

    observer_mock.stop.assert_called_once()
    observer_mock.join.assert_called_once()
