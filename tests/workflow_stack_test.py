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

"""Workflow stack testing of TransportGraph, Lattice and Electron classes."""

import os

import covalent._results_manager.results_manager as rm
from covalent import electron, lattice
from covalent._results_manager.result import Result


@electron
def add(a, b):
    return a + b


@electron
def identity(a):
    return a


@lattice
def check(a, b):
    result1 = add(a=a, b=b)
    return identity(a=result1)


@lattice
def check_alt(a, b):
    result1 = add(a=a, b=b)
    return identity(a=result1)


@electron
def collect(l_electrons):
    return l_electrons


def construct_temp_cache_dir():
    try:
        os.mkdir("/tmp/covalent")
    except FileExistsError:
        pass


def test_electron_components():
    """Test to see if electron preserves the fact that it works as same function after addition
    of electron"""

    assert add(1, 2) == 3


def test_check_nodes():
    """Check if nodes are unique and you have the correct graph
    TODO:ultimately we might want to check if the graph's certain attributes are equal to each
    other"""

    check.build_graph(a=1, b=2)
    assert [0, 1, 2, 3] == list(check.transport_graph._graph.nodes)


def test_electron_takes_nested_iterables():
    """
    Test to check whether electron can take in nested dicts and lists
    """

    @lattice
    def workflow():
        # Use keywords to specify parameters
        a_list = [identity(a=i) for i in range(5)]
        b_list = [identity(a=i) for i in range(5, 10)]
        return collect(l_electrons=[a_list, b_list])

    dispatch_id = workflow.dispatch()

    assert rm.get_result(dispatch_id, wait=True).result == [
        [0, 1, 2, 3, 4],
        [5, 6, 7, 8, 9],
    ]

    rm._delete_result(dispatch_id)


def test_sublatticing():
    """
    Test to check whether an electron can be sublatticed
    and used inside of a bigger lattice.
    """

    sublattice_add = lattice(add)

    @lattice
    def workflow(a, b):
        res_1 = electron(sublattice_add)(a=a, b=b)
        return identity(a=res_1)

    dispatch_id = workflow.dispatch(a=1, b=2)

    workflow_result = rm.get_result(dispatch_id, wait=True)

    assert workflow_result.result == 3
    assert workflow_result.get_node_result(0)["sublattice_result"].result == 3


def test_parallelization():
    """
    Test parallelization of multiple electrons and check if calling the lattice
    normally vs using covalent improves the performance at all.
    """

    # TODO: Maybe a more efficient test can be added to check parallelization

    import timeit

    SETUP_CODE = """
from covalent import electron, lattice

@electron
def heavy_function(a):
    import time

    time.sleep(1)
    return a

@lattice
def workflow(x=10):
    for i in range(x):
        heavy_function(a=i)
    return x
"""

    TEST_CODE_1 = "workflow()"
    TEST_CODE_2 = "workflow.dispatch_sync()"

    time_for_normal = timeit.timeit(
        setup=SETUP_CODE,
        stmt=TEST_CODE_1,
        number=1,
    )

    time_for_covalent = timeit.timeit(
        setup=SETUP_CODE,
        stmt=TEST_CODE_2,
        number=1,
    )

    assert time_for_normal > time_for_covalent


def test_electrons_with_positional_args():
    """
    Test to check whether an electron can be called with positional arguments
    inside a lattice.
    """

    @electron
    def test_func(a, b):
        return a + b

    @lattice
    def workflow(a, b):
        return test_func(a, b)

    dispatch_id = workflow.dispatch(a=1, b=2)

    workflow_result = rm.get_result(dispatch_id, wait=True)

    rm._delete_result(dispatch_id)

    assert workflow_result.result == 3


def test_lattice_with_positional_args():
    """
    Test to check whether the lattice can be dispatched with positional arguments.
    """

    @electron
    def test_func(a, b):
        return a + b

    @lattice
    def workflow(a, b):
        return test_func(a=a, b=b)

    dispatch_id = workflow.dispatch(1, 2)

    workflow_result = rm.get_result(dispatch_id, wait=True)

    rm._delete_result(dispatch_id)

    assert workflow_result.result == 3


def test_positional_args_integration():
    """
    Test whether positional and keyword arguments work together in both lattice and electrons.
    """

    @electron
    def new_func(a, b, c, d, e):
        return a + b + c + d + e

    @lattice
    def work_func(a, b, c):
        return new_func(a, b, c, d=4, e=5)

    dispatch_id = work_func.dispatch(1, 2, c=3)

    workflow_result = rm.get_result(dispatch_id, wait=True)

    rm._delete_result(dispatch_id)

    assert workflow_result.result == 15


def test_stdout_stderr_redirection():
    """
    Test whether stdout and stderr are redirected correctly.
    """
    import sys

    @electron
    def test_func(a, b):
        print(a)
        print(b, file=sys.stderr)
        return a + b

    @lattice
    def work_func(a, b):
        return test_func(a, b)

    dispatch_id = work_func.dispatch(1, 2)

    workflow_result = rm.get_result(dispatch_id, wait=True)

    rm._delete_result(dispatch_id)

    node_results = workflow_result.get_all_node_results()
    stdout = [nr["stdout"] for nr in node_results if nr["stdout"]][0]
    stderr = [nr["stderr"] for nr in node_results if nr["stderr"]][0]

    assert stdout == "1\n"
    assert stderr == "2\n"


def test_decorated_function():
    """
    Test whether covalent works as intended on an already decorated function.
    """

    import pennylane as qml
    from matplotlib import pyplot as plt

    import covalent as ct

    dev1 = qml.device("default.qubit", wires=1)

    @ct.electron
    @qml.qnode(dev1)
    def circuit(params):
        qml.RX(params[0], wires=0)
        qml.RY(params[1], wires=0)
        return qml.expval(qml.PauliZ(0))

    @ct.lattice
    def workflow():
        return circuit([0.54, 0.12])

    dispatch_id = workflow.dispatch()
    workflow_result = rm.get_result(dispatch_id, wait=True)

    rm._delete_result(dispatch_id)

    assert workflow_result.status == Result.COMPLETED


def test_dispatch_cancellation():
    """
    Test whether a running dispatch can be successfully cancelled.
    """

    import time

    @electron
    def task_1():
        time.sleep(4)
        print("Task 1")
        return 5

    @electron
    def task_2(x):
        time.sleep(x)
        print("Task 2")

    @lattice
    def workflow():
        task_2(task_1())
        return 10

    dispatch_id = workflow.dispatch()
    result = rm.get_result(dispatch_id)

    assert result.status in [Result.RUNNING, Result.NEW_OBJ]

    rm.cancel(dispatch_id)

    result = rm.get_result(dispatch_id, wait=True)

    assert result.status == Result.CANCELLED
