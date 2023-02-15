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


import pytest

from covalent.triggers import BaseTrigger, DirTrigger, TimeTrigger
from covalent.triggers.trigger_loader import TriggerLoader


@pytest.fixture
def trigger_loader():
    return TriggerLoader()


def test_trigger_loader_init(mocker, trigger_loader):
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
