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
    return {
        "test_a": "test_func_a",
        "test_b": "test_func_b",
        "test_c": "test_func_c",
        "test_d": "test_func_d",
        "test_e": "test_func_e",
    }


def test_event_handler_init():
    dir_event_handler = DirEventHandler()
    for k, v in dir_event_handler.supported_event_to_func_names.items():
        assert v == f"on_{k}"


def test_attach_methods_to_handler(mocker, event_to_func_names):
    event_handler_mock = mock.Mock()
    event_handler_mock.supported_event_to_func_names = event_to_func_names

    mocker.patch("covalent.triggers.DirTrigger.trigger")
    setattr_mock = mocker.patch("covalent.triggers.dir_trigger.setattr")

    test_dir_path = "test_dir_path"
    test_event_names = list(event_to_func_names.keys())[:4]

    dir_trigger = DirTrigger(test_dir_path, test_event_names)
    dir_trigger.event_handler = event_handler_mock
    dir_trigger.attach_methods_to_handler()

    assert setattr_mock.call_count == len(test_event_names)
