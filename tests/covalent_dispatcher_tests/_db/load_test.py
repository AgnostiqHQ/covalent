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


"""Unit tests for result loading (from database) module."""

from unittest.mock import MagicMock, call

from covalent._shared_files.util_classes import Status
from covalent_dispatcher._db.load import _result_from, get_result_object_from_storage


def test_result_from(mocker):
    """Test the result from function in the load module."""
    mock_lattice_record = MagicMock()
    load_file_mock = mocker.patch("covalent_dispatcher._db.load.load_file")
    lattice_mock = mocker.patch("covalent_dispatcher._db.load.lattice")
    result_mock = mocker.patch("covalent_dispatcher._db.load.Result")

    result_object = _result_from(mock_lattice_record)

    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.function_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.function_string_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.docstring_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.executor_data_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.workflow_executor_data_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.inputs_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.named_args_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.named_kwargs_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.error_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.transport_graph_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.results_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.deps_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.call_before_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.call_after_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.cova_imports_filename,
        )
        in load_file_mock.mock_calls
    )
    assert (
        call(
            storage_path=mock_lattice_record.storage_path,
            filename=mock_lattice_record.lattice_imports_filename,
        )
        in load_file_mock.mock_calls
    )

    lattice_mock.assert_called_once()
    result_mock.assert_called_once()

    assert result_object._root_dispatch_id == mock_lattice_record.root_dispatch_id
    assert result_object._status == Status(mock_lattice_record.status)
    assert result_object._error == load_file_mock.return_value
    assert result_object._inputs == load_file_mock.return_value
    assert result_object._start_time == mock_lattice_record.started_at
    assert result_object._end_time == mock_lattice_record.completed_at
    assert result_object._result == load_file_mock.return_value
    assert result_object._num_nodes == mock_lattice_record.electron_num

    lattice_mock_attrs = lattice_mock().__dict__
    assert set(lattice_mock_attrs.keys()) == {
        "workflow_function",
        "workflow_function_string",
        "__name__",
        "__doc__",
        "metadata",
        "args",
        "kwargs",
        "named_args",
        "named_kwargs",
        "transport_graph",
        "cova_imports",
        "lattice_imports",
        "post_processing",
        "electron_outputs",
    }
    assert lattice_mock_attrs["post_processing"] is False
    assert lattice_mock_attrs["electron_outputs"] == {}

    _, args, _ = lattice_mock.mock_calls[0]
    assert args[0].__name__ == "dummy_function"


def test_get_result_object_from_storage(mocker):
    """Test the get_result_object_from_storage method."""
    result_from_mock = mocker.patch("covalent_dispatcher._db.load._result_from")

    workflow_db_mock = mocker.patch("covalent_dispatcher._db.load.workflow_db")

    result_object = get_result_object_from_storage("mock-dispatch-id")
