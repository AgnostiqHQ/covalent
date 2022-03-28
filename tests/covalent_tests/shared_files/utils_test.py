# Copyright 2021 Agnostiq Inc.
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

"""Unit tests for utils."""

from datetime import timedelta

import pytest

from covalent._shared_files.utils import get_time, get_timedelta, reformat


@pytest.mark.parametrize(
    "time_limit,delta",
    [
        ("1-12:02:31", timedelta(days=1, hours=12, minutes=2, seconds=31)),
        ("0-01:00:00", timedelta(days=0, hours=1, minutes=0, seconds=0)),
    ],
)
def test_get_timedelta(time_limit, delta):
    assert get_timedelta(time_limit) == delta


@pytest.mark.parametrize(
    "value,formatted_value",
    [
        (1, "01"),
        (11, "11"),
    ],
)
def test_reformat(value, formatted_value):
    assert reformat(value) == formatted_value


@pytest.mark.parametrize(
    "delta,delta_str",
    [
        (timedelta(days=1, hours=12, minutes=2, seconds=31), "1-12:02:31"),
        (timedelta(days=0, hours=1, minutes=0, seconds=0), "0-01:00:00"),
    ],
)
def test_get_time(delta, delta_str):
    assert get_time(delta) == delta_str
