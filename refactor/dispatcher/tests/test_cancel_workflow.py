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

"""Unit tests for Cancel Workflow."""

from copy import deepcopy

import pytest

import covalent as ct


class TestCancelWorkflow:
    @pytest.fixture
    def mock_result_construct(self):
        """Construct mock result object."""

        @ct.electron
        def add(x, y):
            return x + y

        @ct.electron
        def multiply(x, y):
            return x * y

        @ct.electron
        def square(x):
            return x**2

        @ct.lattice
        def workflow(x, y, z):
            a = add(x, y)
            b = square(z)
            final = multiply(a, b)
            return final

        lattice = deepcopy(workflow)
        lattice.build_graph(x=1, y=2, z=3)
        lattice.transport_graph = lattice.transport_graph.serialize()

        return lattice.electron_outputs

    def test_cancel_workflow_execution(
        self,
        mock_result_construct,
    ):

        return mock_result_construct

    def test_cancel_task(self):
        # This will test cancel_task()
        pass

    def test_get_all_task_ids(self):
        # This will test the get_all_task_ids()
        pass
