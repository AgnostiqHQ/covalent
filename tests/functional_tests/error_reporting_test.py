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

"""FT to check that workflow errors are reported correctly"""

import covalent as ct
from covalent._results_manager import Result


@ct.electron(executor="local")
def failing_task_0():
    import sys

    print("Hello from Task 0", file=sys.stdout)
    print("Hello from Task 0", file=sys.stderr)
    raise RuntimeError("Error 0")


@ct.electron(executor="local")
def failing_task_1():
    import sys

    print("Hello from Task 1", file=sys.stdout)


@ct.electron(executor="nonexistent")
def bad_exec_task():
    pass


@ct.electron(executor="local")
@ct.lattice
def failing_task_2():
    failing_task_1()
    failing_task_1()


@ct.electron(executor="local")
def failing_task_3():
    raise RuntimeError("Error 3")


def test_task_runtime_error_reporting():
    """Check handling of task runtime errors"""

    @ct.lattice
    def workflow():
        failing_task_0()
        failing_task_1()

    dispatch_id = ct.dispatch(workflow)()
    res = ct.get_result(dispatch_id, wait=True)

    assert res.status == Result.FAILED
    tg = res.lattice.transport_graph
    assert tg.get_node_value(0, "status") == Result.FAILED
    assert tg.get_node_value(0, "stdout") == "Hello from Task 0\n"
    assert tg.get_node_value(0, "stderr").startswith("Hello from Task 0\n")
    assert "RuntimeError" in tg.get_node_value(0, "stderr")
    assert tg.get_node_value(1, "status") == Result.COMPLETED
    assert tg.get_node_value(1, "stdout") == "Hello from Task 1\n"


def test_task_covalent_error_reporting():
    """Check handling of task-specific errors from Covalent"""

    @ct.lattice
    def workflow():
        bad_exec_task()

    dispatch_id = ct.dispatch(workflow)()
    res = ct.get_result(dispatch_id, wait=True)

    assert res.status == Result.FAILED
    tg = res.lattice.transport_graph
    assert "nonexistent" in tg.get_node_value(0, "error")
