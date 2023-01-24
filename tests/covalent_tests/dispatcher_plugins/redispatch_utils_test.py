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

"""Unit tests for redispatch utils module in dispatcher_plugins."""

import pytest

import covalent as ct
from covalent._dispatcher_plugins.redispatch_utils import (
    _filter_null_metadata,
    _generate_electron_updates,
    _get_transportable_electron,
)
from covalent._shared_files.context_managers import active_lattice_manager
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

    @ct.lattice
    def workflow():
        pass

    # Construct bound electrons, i.e. electron with non-null function and node_id
    identity_electron = Electron(function=identity, node_id=1, metadata={"executor": "local"})
    add_electron = Electron(function=add, node_id=2, metadata={"executor": "local"})

    with active_lattice_manager.claim(workflow):
        electron_updates = _generate_electron_updates(
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


def test_get_request_body():
    """Test the get request body function."""
    pass
