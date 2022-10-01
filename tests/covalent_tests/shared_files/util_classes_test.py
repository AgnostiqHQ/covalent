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

# import queue
import asyncio
from unittest import mock

import pytest

from covalent._shared_files.util_classes import AsyncSafeVariable, Status


@pytest.fixture
def test_value():
    return 42


@pytest.fixture
def safe_variable():
    return AsyncSafeVariable()


def test_legacy_status():
    """Testing whether the legacy Status class works as expected"""

    test_status_str = "TEST_STATUS"
    legacy_status = Status(test_status_str)

    assert legacy_status.STATUS == test_status_str
    assert str(legacy_status) == test_status_str


def test_safe_variable_init():
    """Testing AsyncSafeVariable's initialization"""

    safe_variable = AsyncSafeVariable()
    assert safe_variable.maxsize == 1


def test_safe_variable_save(mocker: mock, test_value: int, safe_variable: AsyncSafeVariable):
    """Testing AsyncSafeVariable's save method"""

    put_nowait_mock = mocker.patch(
        "covalent._shared_files.util_classes.AsyncSafeVariable.put_nowait"
    )

    safe_variable.save(test_value)
    put_nowait_mock.assert_called_with(test_value)


def test_safe_variable_save_exception(
    mocker: mock, test_value: int, safe_variable: AsyncSafeVariable
):
    """Testing AsyncSafeVariable's save method when queue is full"""

    put_nowait_mock = mocker.patch(
        "covalent._shared_files.util_classes.AsyncSafeVariable.put_nowait"
    )
    put_nowait_mock.side_effect = asyncio.QueueFull

    get_nowait_mock = mocker.patch(
        "covalent._shared_files.util_classes.AsyncSafeVariable.get_nowait"
    )

    def remove_side_effect_after_getting():
        put_nowait_mock.side_effect = None

    get_nowait_mock.side_effect = remove_side_effect_after_getting

    safe_variable.save(test_value + 1)

    get_nowait_mock.assert_called_once()
    put_nowait_mock.assert_called_with(test_value + 1)


def test_safe_variable_retrieve(mocker: mock, test_value: int, safe_variable: AsyncSafeVariable):
    """Testing AsyncSafeVariable's retrieve method"""

    get_nowait_mock = mocker.patch(
        "covalent._shared_files.util_classes.AsyncSafeVariable.get_nowait"
    )
    get_nowait_mock.return_value = test_value

    put_nowait_mock = mocker.patch(
        "covalent._shared_files.util_classes.AsyncSafeVariable.put_nowait"
    )

    value = safe_variable.retrieve()
    assert value == test_value
    get_nowait_mock.assert_called_once()
    put_nowait_mock.assert_called_with(test_value)


def test_safe_variable_retrieve_exception(mocker: mock, safe_variable: AsyncSafeVariable):
    """Testing AsyncSafeVariable's retrieve method when queue is empty"""

    get_nowait_mock = mocker.patch(
        "covalent._shared_files.util_classes.AsyncSafeVariable.get_nowait"
    )
    get_nowait_mock.side_effect = asyncio.QueueEmpty

    put_nowait_mock = mocker.patch(
        "covalent._shared_files.util_classes.AsyncSafeVariable.put_nowait"
    )

    value = safe_variable.retrieve()

    assert value is None

    get_nowait_mock.assert_called_once()
    put_nowait_mock.call_count == 0


@pytest.mark.asyncio
async def test_safe_variable_retrieve_wait(
    mocker: mock, test_value: int, safe_variable: AsyncSafeVariable
):
    """Testing AsyncSafeVariable's retrieve_async method"""

    get_mock = mocker.patch(
        "covalent._shared_files.util_classes.AsyncSafeVariable.get", return_value=test_value
    )

    put_mock = mocker.patch("covalent._shared_files.util_classes.AsyncSafeVariable.put")

    value = await safe_variable.retrieve_wait()
    get_mock.assert_called_once()
    put_mock.assert_called_with(test_value)
    assert value == test_value
