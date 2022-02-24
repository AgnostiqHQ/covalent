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

import covalent as ct
import covalent._results_manager.results_manager as rm
from covalent._results_manager.result import Result


@ct.electron
def add(a, b):
    return a + b


@ct.electron
def identity(a):
    return a


@ct.lattice
def check(a, b):
    result1 = add(a=a, b=b)
    return identity(a=result1)


@ct.lattice
def check_alt(a, b):
    result1 = add(a=a, b=b)
    return identity(a=result1)


@ct.electron
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

    @ct.lattice
    def workflow():
        # Use keywords to specify parameters
        a_list = [identity(a=i) for i in range(5)]
        b_list = [identity(a=i) for i in range(5, 10)]
        return collect(l_electrons=[a_list, b_list])

    dispatch_id = ct.dispatch(workflow)()

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

    sublattice_add = ct.lattice(add)

    @ct.lattice
    def workflow(a, b):
        res_1 = ct.electron(sublattice_add)(a=a, b=b)
        return identity(a=res_1)

    dispatch_id = ct.dispatch(workflow)(a=1, b=2)

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
import covalent as ct

@ct.electron
def heavy_function(a):
    import time

    time.sleep(1)
    return a

@ct.lattice
def workflow(x=10):
    for i in range(x):
        heavy_function(a=i)
    return x
"""

    TEST_CODE_1 = "workflow()"
    TEST_CODE_2 = "ct.dispatch_sync(workflow)()"

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

    @ct.electron
    def test_func(a, b):
        return a + b

    @ct.lattice
    def workflow(a, b):
        return test_func(a, b)

    dispatch_id = ct.dispatch(workflow)(a=1, b=2)

    workflow_result = rm.get_result(dispatch_id, wait=True)

    rm._delete_result(dispatch_id)

    assert workflow_result.result == 3


def test_lattice_with_positional_args():
    """
    Test to check whether the lattice can be dispatched with positional arguments.
    """

    @ct.electron
    def test_func(a, b):
        return a + b

    @ct.lattice
    def workflow(a, b):
        return test_func(a=a, b=b)

    dispatch_id = ct.dispatch(workflow)(1, 2)

    workflow_result = rm.get_result(dispatch_id, wait=True)

    rm._delete_result(dispatch_id)

    assert workflow_result.result == 3


def test_positional_args_integration():
    """
    Test whether positional and keyword arguments work together in both lattice and electrons.
    """

    @ct.electron
    def new_func(a, b, c, d, e):
        return a + b + c + d + e

    @ct.lattice
    def work_func(a, b, c):
        return new_func(a, b, c, d=4, e=5)

    dispatch_id = ct.dispatch(work_func)(1, 2, c=3)

    workflow_result = rm.get_result(dispatch_id, wait=True)

    rm._delete_result(dispatch_id)

    assert workflow_result.result == 15


def test_stdout_stderr_redirection():
    """
    Test whether stdout and stderr are redirected correctly.
    """
    import sys

    @ct.electron
    def test_func(a, b):
        print(a)
        print(b, file=sys.stderr)
        return a + b

    @ct.lattice
    def work_func(a, b):
        return test_func(a, b)

    dispatch_id = ct.dispatch(work_func)(1, 2)

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

    dispatch_id = ct.dispatch(workflow)()
    workflow_result = rm.get_result(dispatch_id, wait=True)

    rm._delete_result(dispatch_id)

    assert workflow_result.status == Result.COMPLETED


def test_dispatch_cancellation():
    """
    Test whether a running dispatch can be successfully cancelled.
    """

    import numpy as np

    rng = np.random.default_rng()

    @ct.electron
    def generate_random_list(size):
        return rng.choice(size, size=size, replace=False)

    @ct.electron
    def get_sorted(unsorted_list):
        return np.sort(unsorted_list)

    @ct.lattice
    def workflow(size=100_000_00, repetitions=10):
        for _ in range(repetitions):
            get_sorted(generate_random_list(size))
        return repetitions

    dispatch_id = ct.dispatch(workflow)()
    result = rm.get_result(dispatch_id)

    assert result.status in [Result.RUNNING, Result.NEW_OBJ]

    rm.cancel(dispatch_id)

    result = rm.get_result(dispatch_id, wait=True)

    rm._delete_result(dispatch_id)

    assert result.status == Result.CANCELLED


def test_all_parameter_types_in_electron():
    """Test whether an electron supports parameter passing in every python compatible way"""

    @ct.electron
    def task(a, /, b, *args, c, **kwargs):
        return a * b * c, args, kwargs

    @ct.lattice
    def workflow():
        return task(1, 2, 3, 4, c=5, d=6, e=7)

    dispatch_id = ct.dispatch(workflow)()
    result = rm.get_result(dispatch_id, wait=True)
    rm._delete_result(dispatch_id)

    assert result.result == (10, (3, 4), {"d": 6, "e": 7})


def test_all_parameter_types_in_lattice():
    """Test whether a lattice supports parameter passing in every python compatible way"""

    @ct.electron
    def task(a, /, b, *args, c, **kwargs):
        return a * b * c, args, kwargs

    @ct.lattice
    def workflow(a, /, b, *args, c, **kwargs):
        return task(a, b, *args, c=c, **kwargs)

    dispatch_id = ct.dispatch(workflow)(1, 2, 3, 4, c=5, d=6, e=7)
    result = rm.get_result(dispatch_id, wait=True)
    rm._delete_result(dispatch_id)

    assert result.inputs["args"] == [1, 2, 3, 4]
    assert result.inputs["kwargs"] == {"c": 5, "d": 6, "e": 7}

    assert result.result == (10, (3, 4), {"d": 6, "e": 7})
