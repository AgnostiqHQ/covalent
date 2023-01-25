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

"""Unit/integration tests for redispatch utils module in dispatcher_plugins."""

import pytest

import covalent as ct
from covalent._dispatcher_plugins.redispatch_utils import (
    _filter_null_metadata,
    _get_transportable_electron,
    get_electron_objects,
    get_request_body,
)
from covalent._workflow.electron import Electron
from covalent._workflow.transport import TransportableObject


@pytest.mark.parametrize(
    "meta_dict,expected",
    [
        ({}, {}),
        ({"a": 1}, {"a": 1}),
        ({"a": 1, "b": None}, {"a": 1}),
    ],
)
def test_filter_null_metadata(meta_dict, expected):
    """Test the filter null metadata function."""
    filtered = _filter_null_metadata(meta_dict)
    assert filtered == expected


def test_get_transportable_electron(mocker):
    """Test the get transportable electron function."""
    mocker.patch(
        "covalent._dispatcher_plugins.redispatch_utils.get_serialized_function_str",
        return_value="mock-function-string",
    )
    mocker.patch(
        "covalent._dispatcher_plugins.redispatch_utils._filter_null_metadata",
        return_value="mock-metadata",
    )

    @ct.electron
    def test_func(a):
        return a

    # Construct bound electron, i.e. electron with non-null function and node_id
    electron = Electron(function=test_func, node_id=1, metadata={"a": 1, "b": 2})
    transportable_electron = _get_transportable_electron(electron)

    assert transportable_electron["name"] == "test_func"
    assert transportable_electron["metadata"] == "mock-metadata"
    assert transportable_electron["function_string"] == "mock-function-string"
    assert TransportableObject(test_func).to_dict() == transportable_electron["function"]


def test_generate_electron_updates(mocker):
    """Test the generate electron updates function."""
    mocker.patch(
        "covalent._dispatcher_plugins.redispatch_utils._get_transportable_electron",
        side_effect=["mock-transportable-electron-1", "mock-transportable-electron-2"],
    )

    @ct.electron
    def identity(a):
        return a

    @ct.electron
    def add(a, b):
        return a + b

    electron_updates = get_electron_objects(
        "mock-dispatch-id",
        {
            "mock_task_id_1": identity,
            "mock_task_id_2": add,
        },
    )
    assert electron_updates == {
        "mock_task_id_1": "mock-transportable-electron-1",
        "mock_task_id_2": "mock-transportable-electron-2",
    }


def test_integration_generate_electron_updates():
    """Test the generate electron updates function."""

    @ct.electron
    def identity(a):
        return a

    @ct.electron
    def add(a, b):
        return a + b

    electron_updates = get_electron_objects(
        "mock-dispatch-id",
        {
            "mock_task_id_1": identity,
            "mock_task_id_2": add,
        },
    )
    assert electron_updates["mock_task_id_1"]["name"] == "identity"
    assert electron_updates["mock_task_id_2"]["name"] == "add"


def test_get_request_body_null_arguments():
    """Test the get request body function with null arguments."""

    @ct.electron
    def identity(a):
        return a

    @ct.electron
    def add(a, b):
        return a + b

    response = get_request_body(
        "mock-dispatch-id",
    )
    assert response == {
        "json_lattice": None,
        "dispatch_id": "mock-dispatch-id",
        "electron_updates": {},
        "reuse_previous_results": False,
    }


def test_get_request_body_args_kwargs(mocker):
    """Test the get request body function when args/kwargs is not null."""
    generate_electron_updates_mock = mocker.patch(
        "covalent._dispatcher_plugins.redispatch_utils._generate_electron_updates",
        return_value="mock-electron-updates",
    )
    get_result_mock = mocker.patch("covalent._dispatcher_plugins.redispatch_utils.get_result")
    get_result_mock().lattice.serialize_to_json.return_value = "mock-json-lattice"

    response = get_request_body(
        "mock-dispatch-id",
        new_args=[1, 2],
        new_kwargs={"a": 1, "b": 2},
        replace_electrons={"mock-task-id": "mock-electron"},
    )
    generate_electron_updates_mock.assert_called_once_with(
        "mock-dispatch-id", {"mock-task-id": "mock-electron"}
    )
    assert response == {
        "json_lattice": "mock-json-lattice",
        "dispatch_id": "mock-dispatch-id",
        "electron_updates": "mock-electron-updates",
        "reuse_previous_results": False,
    }
    get_result_mock().lattice.build_graph.assert_called_once_with(*[1, 2], **{"a": 1, "b": 2})
