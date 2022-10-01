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

from unittest import mock

import pytest

from covalent._shared_files.util_classes import SafeVariable, Status


@pytest.fixture
def test_value():
    return 42


@pytest.fixture
def safe_variable():
    return SafeVariable()


def test_legacy_status():
    """Testing whether the legacy Status class works as expected"""

    test_status_str = "TEST_STATUS"
    legacy_status = Status(test_status_str)

    assert legacy_status.STATUS == test_status_str
    assert str(legacy_status) == test_status_str


def test_safe_variable_init():
    """Testing SafeVariable's initialization"""

    safe_variable = SafeVariable()
    assert safe_variable.maxsize == 1


@pytest.mark.parametrize("is_full", [False, True])
def test_safe_variable_save(
    mocker: mock, test_value: int, safe_variable: SafeVariable, is_full: bool
):
    """Testing SafeVariable's save method"""

    full_mock = mocker.patch("covalent._shared_files.util_classes.SafeVariable.full")
    full_mock.return_value = is_full

    put_mock = mocker.patch("covalent._shared_files.util_classes.SafeVariable.put")

    get_mock = mocker.patch("covalent._shared_files.util_classes.SafeVariable.get")

    if not is_full:
        safe_variable.save(test_value)

        put_mock.assert_called_with(test_value)

    else:
        safe_variable.save(test_value + 1)

        get_mock.assert_called_once()
        put_mock.assert_called_with(test_value + 1)


@pytest.mark.parametrize("is_empty", [False, True])
def test_safe_variable_retrieve(
    mocker: mock, test_value: int, safe_variable: SafeVariable, is_empty: bool
):
    """Testing SafeVariable's retrieve method"""

    empty_mock = mocker.patch("covalent._shared_files.util_classes.SafeVariable.empty")
    empty_mock.return_value = is_empty

    get_mock = mocker.patch(
        "covalent._shared_files.util_classes.SafeVariable.get", return_value=test_value
    )

    put_mock = mocker.patch("covalent._shared_files.util_classes.SafeVariable.put")

    value = safe_variable.retrieve()

    if not is_empty:
        assert value == test_value
        get_mock.assert_called_once()
        put_mock.assert_called_with(test_value)

    else:
        assert value is None
        get_mock.call_count == 0
        put_mock.call_count == 0
