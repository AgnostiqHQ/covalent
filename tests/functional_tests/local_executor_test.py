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


import covalent as ct
import covalent._results_manager.results_manager as rm
from covalent._results_manager.result import Result


def test_local_executor_returns_stdout_stderr():
    from covalent.executor import LocalExecutor

    le = LocalExecutor()

    @ct.electron(executor=le)
    def task(x):
        import sys

        print("Hello")
        print("Error", file=sys.stderr)
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    dispatch_id = ct.dispatch(workflow)(5)
    res = ct.get_result(dispatch_id, wait=True)
    tg = res.lattice.transport_graph
    assert tg.get_node_value(0, "stdout") == "Hello\n"
    assert tg.get_node_value(0, "stderr") == "Error\n"
    assert tg.get_node_value(0, "output").get_deserialized() == 5


def test_local_executor_build_sublattice_graph():
    """
    Check using local executor to build_sublattice_graph.

    This will exercise the /register endpoint for sublattices.
    """

    def add(a, b):
        return a + b

    @ct.electron(executor="local")
    def identity(a):
        return a

    sublattice_add = ct.lattice(add)

    @ct.lattice(executor="local", workflow_executor="local")
    def workflow(a, b):
        res_1 = ct.electron(sublattice_add, executor="local")(a=a, b=b)
        return identity(a=res_1)

    dispatch_id = ct.dispatch(workflow)(a=1, b=2)
    workflow_result = rm.get_result(dispatch_id, wait=True)

    assert workflow_result.error == ""
    assert workflow_result.status == Result.COMPLETED
    assert workflow_result.result == 3
    assert workflow_result.get_node_result(node_id=0)["sublattice_result"].result == 3
