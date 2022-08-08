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

"""Tests for results manager."""

from unittest import result

import pytest

from covalent._data_store.models import Lattice
from covalent._results_manager.results_manager import result_from


@pytest.fixture
def lattice_record():
    return Lattice(
        id=1,
        dispatch_id="mock_dispatch_id",
        name="mock_name",
        status="mock_status",
        electron_num="mock_electron_num",
        completed_electron_num="mock_completed_electron_num",
        storage_type="local",
        storage_path="mock_storage_path",
        function_filename="mock_function_filename",
        function_string_filename="mock_function_string_filename",
        executor_data_filename="mock_executor_data_filename",
        error_filename="mock_error_filename",
        inputs_filename="mock_inputs_filename",
        results_filename="mock_results_filename",
        transport_graph_filename="mock_transport_graph_filename",
        is_active=True,
        created_at=None,
        updated_at=None,
        started_at=None,
        completed_at=None,
    )


def test_result_from(lattice_record, mocker):
    """Test the method to rehydrate a result object from a lattice record."""

    mock_load_file = mocker.patch("covalent._results_manager.results_manager.load_file")
    result_from(lattice_record)
    mock_load_file.assert_called()
