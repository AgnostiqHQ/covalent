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
from pathlib import Path

import pytest

from covalent.cloud_resource_manager.core import (
    CloudResourceManager,
    get_converted_value,
    get_executor_module,
    validate_options,
)


def test_get_executor_module(mocker):
    test_executor_name = "test_executor"
    test_executor_module = "test_executor_module"

    mock_import_module = mocker.patch(
        "covalent.cloud_resource_manager.core.importlib.import_module",
        return_value=test_executor_module,
    )

    mocker.patch(
        "covalent.cloud_resource_manager.core._executor_manager.executor_plugins_map",
        return_value={test_executor_name: "test"},
    )

    returned_module = get_executor_module(test_executor_name)

    assert returned_module == test_executor_module
    mock_import_module.assert_called_once()


@pytest.mark.parametrize(
    "value, expected",
    [
        ("true", True),
        ("false", False),
        ("null", None),
        ("1", 1),
        ("1.0", 1.0),
        ("test", "test"),
    ],
)
def test_get_converted_value(value, expected):
    assert get_converted_value(value) == expected


def test_validate_options(mocker):
    executor_options = {"test_key": "test_value"}
    executor_name = "test_executor"

    mock_get_executor_module = mocker.patch(
        "covalent.cloud_resource_manager.core.get_executor_module",
    )

    mock_defaults_model = mocker.MagicMock()
    mocker.patch(
        "covalent.cloud_resource_manager.core.getattr",
        return_value=mock_defaults_model,
    )

    mock_list = mocker.patch(
        "covalent.cloud_resource_manager.core.list",
        return_value=list(executor_options.keys()),
    )

    validate_options(executor_options, executor_name)

    mock_get_executor_module.assert_called_once_with(executor_name)

    assert mock_list.call_count == 2

    mock_defaults_model.assert_any_call(**executor_options)
    assert mock_defaults_model.call_count == 2


@pytest.mark.parametrize(
    "options",
    [
        None,
        {"test_key": "test_value"},
    ],
)
def test_cloud_resource_manager_init(mocker, options):
    test_executor_name = "test_executor"
    test_executor_module_path = "test_executor_module_path"

    mock_validate_options = mocker.patch(
        "covalent.cloud_resource_manager.core.validate_options",
    )

    crm = CloudResourceManager(
        executor_name=test_executor_name,
        executor_module_path=test_executor_module_path,
        options=options,
    )

    assert crm.executor_name == test_executor_name
    assert crm.executor_tf_path == str(
        Path(test_executor_module_path).expanduser().resolve() / "assets" / "infra"
    )
    assert crm.executor_options == options

    if options:
        mock_validate_options.assert_called_once_with(options, test_executor_name)
    else:
        mock_validate_options.assert_not_called()


def test_print_stdout(mocker):
    test_stdout = "test_stdout".encode("utf-8")
    test_return_code = 0

    mock_process = mocker.MagicMock()

    mock_process.poll.side_effect = partial(next, iter([None, test_return_code, test_return_code]))
    mock_process.stdout.readline.side_effect = partial(next, iter([test_stdout, None]))

    mock_print = mocker.patch("covalent.cloud_resource_manager.core.print")

    crm = CloudResourceManager(
        executor_name="test_executor",
        executor_module_path="test_executor_module_path",
    )

    return_code = crm._print_stdout(mock_process)

    mock_process.stdout.readline.assert_called_once()
    mock_print.assert_called_once_with(test_stdout.decode("utf-8"))
    assert mock_process.poll.call_count == 3
    assert return_code == test_return_code
