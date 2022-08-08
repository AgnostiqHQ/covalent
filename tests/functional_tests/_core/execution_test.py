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

"""
Functional test for the core functionality of the dispatcher.
"""

import pytest

import covalent as ct
from covalent_dispatcher._core.execution import _run_task


@ct.electron
def a(x):
    return x, x**2


@ct.lattice
def p(x):
    result, b = a(x=x)
    for _ in range(1):
        result, b = a(x=result)
    return b, result


@pytest.fixture
def sublattice_workflow():
    @ct.electron
    @ct.lattice
    def sublattice(x):
        res = a(x)
        return res

    @ct.lattice
    def parent_workflow(x):
        res = sublattice(x)
        return res

    parent_workflow.build_graph(x=1)
    return parent_workflow


@pytest.mark.asyncio
async def test_run_task(mocker, sublattice_workflow):
    """Note: This is not a full unit test for the _run_task method. Rather, this is intended to test the diff introduced to write the sublattice electron id in the Database."""

    # class MockResult:
    #     dispatch_id = "test"

    # def mock_func():
    #     return MockResult()
    # class MockSerializedCallable:
    #     def get_deserialized(self):
    #         return mock_func

    from concurrent.futures import ThreadPoolExecutor

    tasks_pool = ThreadPoolExecutor()

    write_sublattice_electron_id_mock = mocker.patch(
        "covalent_dispatcher._core.execution.write_sublattice_electron_id"
    )

    ct.dispatch(sublattice_workflow)(1)

    await _run_task(
        node_id=1,
        dispatch_id="parent_dispatch_id",
        results_dir="/tmp",
        inputs={"args": [], "kwargs": {"x": ct.TransportableObject(1)}},
        serialized_callable=sublattice_workflow.transport_graph.get_node_value(
            0,
            "function",
        ),
        selected_executor=["local", {}],
        call_before=[],
        call_after=[],
        node_name=":sublattice:sublattice",
        tasks_pool=tasks_pool,
        workflow_executor=["local", {}],
    )

    write_sublattice_electron_id_mock.assert_called_once()
