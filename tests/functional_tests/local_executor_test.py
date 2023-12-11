# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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

    assert workflow_result.error is None
    assert workflow_result.status == Result.COMPLETED
    assert workflow_result.result == 3
    assert workflow_result.get_node_result(node_id=0)["sublattice_result"].result == 3
