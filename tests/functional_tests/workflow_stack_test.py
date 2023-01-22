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

import pytest

import covalent as ct
import covalent._results_manager.results_manager as rm
from covalent._results_manager.result import Result
from covalent_dispatcher._db import update


def construct_temp_cache_dir():
    os.makedirs("/tmp/covalent", exist_ok=True)


def test_electron_components():
    """Test to see if electron preserves the fact that it works as same function after addition
    of electron"""

    @ct.electron
    def add(a, b):
        return a + b

    assert add(1, 2) == 3


def test_check_nodes():
    """Check if nodes are unique and you have the correct graph
    TODO:ultimately we might want to check if the graph's certain attributes are equal to each
    other"""

    @ct.electron
    def identity(a):
        return a

    @ct.electron
    def add(a, b):
        return a + b

    @ct.lattice
    def check(a, b):
        result1 = add(a=a, b=b)
        return identity(a=result1)

    check.build_graph(a=1, b=2)

    # Account for the postprocess electrons
    assert [0, 1, 2, 3, 4, 5] == list(check.transport_graph._graph.nodes)


def test_electron_takes_nested_iterables():
    """
    Test to check whether electron can take in nested dicts and lists
    """

    @ct.electron
    def identity(a):
        return a

    @ct.electron
    def collect(l_electrons):
        return l_electrons

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

    def add(a, b):
        return a + b

    @ct.electron
    def identity(a):
        return a

    sublattice_add = ct.lattice(add)

    @ct.lattice
    def workflow(a, b):
        res_1 = ct.electron(sublattice_add)(a=a, b=b)
        return identity(a=res_1)

    dispatch_id = ct.dispatch(workflow)(a=1, b=2)
    workflow_result = rm.get_result(dispatch_id, wait=True)

    assert workflow_result.error is None
    assert workflow_result.status == Result.COMPLETED
    assert workflow_result.result == 3
    assert workflow_result.get_node_result(node_id=0)["sublattice_result"].result == 3


def test_lattice_electron_metadata_propagation():
    """
    Check whether lattice metadata is propagated correctly to electrons
    """

    e_bash_dep = ct.DepsBash(["ls"])
    l_bash_dep = ct.DepsBash(["ls -l"])

    @ct.electron(deps_bash=e_bash_dep)
    def task_1():
        pass

    @ct.electron
    def task_2():
        pass

    @ct.lattice(deps_bash=l_bash_dep)
    def workflow():
        task_1()
        task_2()

    dispatch_id = ct.dispatch(workflow)()
    res = ct.get_result(dispatch_id, wait=True)
    tg = res.lattice.transport_graph

    dep_0 = ct.DepsBash().from_dict(tg.get_node_value(0, "metadata")["deps"]["bash"])
    dep_1 = ct.DepsBash().from_dict(tg.get_node_value(1, "metadata")["deps"]["bash"])

    assert dep_0.commands == ["ls"]
    assert dep_1.commands == ["ls -l"]
    rm._delete_result(dispatch_id)


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


def test_electron_deps_bash():
    import tempfile
    from pathlib import Path

    f = tempfile.NamedTemporaryFile(delete=True)
    tmp_path = f.name
    f.close()

    cmd = f"touch {tmp_path}"

    @ct.electron(deps_bash=ct.DepsBash([cmd]))
    def func(x):
        return x

    @ct.lattice
    def workflow(x):
        return func(x)

    dispatch_id = ct.dispatch(workflow)(x=5)
    res = ct.get_result(dispatch_id, wait=True)

    assert res.result == 5
    assert Path(tmp_path).is_file()

    rm._delete_result(dispatch_id)
    Path(tmp_path).unlink()


def test_electron_deps_call_before():
    import tempfile
    from pathlib import Path

    def create_tmp_file(file_path, **kwargs):
        with open(file_path, "w") as f:
            f.write("Hello")

    f = tempfile.NamedTemporaryFile(delete=True)
    tmp_path = f.name
    f.close()

    def delete_tmp_file(file_path):
        Path(file_path).unlink()

    @ct.electron(
        call_before=[ct.DepsCall(create_tmp_file, args=[tmp_path])],
        call_after=ct.DepsCall(delete_tmp_file, args=[tmp_path]),
    )
    def func(file_path):
        with open(file_path, "r") as f:
            contents = f.read()
        return Path(file_path).is_file(), contents

    @ct.lattice
    def workflow(file_path):
        return func(file_path)

    dispatch_id = ct.dispatch(workflow)(file_path=tmp_path)
    res = ct.get_result(dispatch_id, wait=True)

    assert res.error is None

    assert res.result == (True, "Hello")

    assert not Path(tmp_path).is_file()


def test_electron_deps_inject_calldep_retval():
    def identity(y):
        return y

    calldep = ct.DepsCall(identity, args=[5], retval_keyword="y")

    @ct.electron(call_before=[calldep])
    def task(x, y=0):
        return (x, y)

    @ct.lattice
    def workflow(x):
        return task(x)

    dispatch_id = ct.dispatch(workflow)(2)

    result_object = ct.get_result(dispatch_id, wait=True)

    rm._delete_result(dispatch_id)
    assert result_object.result == (2, 5)


def test_electron_deps_inject_non_unique_calldep_retvals():
    def identity(y):
        return y

    calldep_one = ct.DepsCall(identity, args=[1], retval_keyword="y")
    calldep_two = ct.DepsCall(identity, args=[2], retval_keyword="y")
    calldep_three = ct.DepsCall(identity, args=[3], retval_keyword="y")

    @ct.electron(call_before=[calldep_one, calldep_two, calldep_three])
    def task(y=[]):
        return y

    @ct.lattice
    def workflow():
        return task()

    dispatch_id = ct.dispatch(workflow)()

    result_object = ct.get_result(dispatch_id, wait=True)

    rm._delete_result(dispatch_id)
    assert result_object.result == [1, 2, 3]


def test_electron_deps_pip():

    import subprocess

    @ct.electron(deps_pip=ct.DepsPip(packages=["pydash==5.1.0"]))
    def func(x):
        return x

    @ct.lattice
    def workflow(x):
        return func(x)

    dispatch_id = ct.dispatch(workflow)(x=5)
    res = ct.get_result(dispatch_id, wait=True)

    assert res.result == 5

    import pydash

    assert pydash.__version__ == "5.1.0"

    subprocess.run(
        "pip uninstall -y --no-input pydash",
        shell=True,
        stdin=subprocess.DEVNULL,
        capture_output=True,
    )


def test_electron_deps_bash_implicit():
    import tempfile
    from pathlib import Path

    f = tempfile.NamedTemporaryFile(delete=True)
    tmp_path = f.name
    f.close()

    cmd = f"touch {tmp_path}"

    @ct.electron(deps_bash=[cmd])
    def func(x):
        return x

    @ct.lattice
    def workflow(x):
        return func(x)

    dispatch_id = ct.dispatch(workflow)(x=5)
    res = ct.get_result(dispatch_id, wait=True)

    assert res.result == 5
    assert Path(tmp_path).is_file()

    rm._delete_result(dispatch_id)
    Path(tmp_path).unlink()


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

    node_results = workflow_result.get_all_node_results()
    stdout = [nr["stdout"] for nr in node_results if nr["stdout"]][0]
    stderr = [nr["stderr"] for nr in node_results if nr["stderr"]][0]

    assert stdout == "1\n"
    assert stderr == "2\n"

    rm._delete_result(dispatch_id)


def test_decorated_function():
    """
    Test whether covalent works as intended on an already decorated function.
    """

    import pennylane as qml

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


def test_leaf_electron_failure():
    @ct.electron
    def failing_task():
        assert False

    @ct.lattice
    def workflow():
        failing_task()
        return 1

    dispatch_id = ct.dispatch(workflow)()
    workflow_result = rm.get_result(dispatch_id, wait=True)
    rm._delete_result(dispatch_id)

    tg = workflow_result.lattice.transport_graph

    assert workflow_result.status == Result.FAILED
    assert tg.get_node_value(0, "status") == Result.FAILED


def test_intermediate_electron_failure():
    @ct.electron
    def failing_task(x):
        assert False

    @ct.lattice
    def workflow(x):
        res1 = failing_task(x)
        res2 = failing_task(res1)
        return res2

    dispatch_id = ct.dispatch(workflow)(5)
    workflow_result = rm.get_result(dispatch_id, wait=True)
    rm._delete_result(dispatch_id)

    tg = workflow_result.lattice.transport_graph

    assert workflow_result.status == Result.FAILED
    assert tg.get_node_value(0, "status") == Result.FAILED


@pytest.mark.skip(reason="Inconsistent outcomes")
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

    assert ct.TransportableObject.deserialize_list(result.inputs["args"]) == [1, 2, 3, 4]
    assert ct.TransportableObject.deserialize_dict(result.inputs["kwargs"]) == {
        "c": 5,
        "d": 6,
        "e": 7,
    }

    assert result.result == (10, (3, 4), {"d": 6, "e": 7})


@pytest.mark.skip
def test_client_workflow_executor():
    """
    Test setting `workflow_executor="client"`
    """

    @ct.electron
    def new_func(a, b, c, d, e):
        return a + b + c + d + e

    @ct.lattice(workflow_executor="client")
    def work_func(a, b, c):
        return new_func(a, b, c, d=4, e=5)

    dispatch_id = ct.dispatch(work_func)(1, 2, c=3)

    workflow_result = rm.get_result(dispatch_id, wait=True)
    assert workflow_result.status == Result.PENDING_POSTPROCESSING
    assert workflow_result.result is None
    update.persist(workflow_result)
    assert workflow_result.post_process() == 15
    rm._delete_result(dispatch_id)


def test_two_iterations():
    """Confirm we can build the graph with more than one iteration"""

    @ct.electron
    def split(s, n):
        return s[:n], s[n:]

    @ct.lattice
    def midword(a, b, n):
        first, last = split(a, n)
        return first + b + last

    midword.build_graph("hello world", "beautiful", 6)

    # Account for pp electrons
    assert [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] == list(midword.transport_graph._graph.nodes)


def test_two_iterations_float():
    """Confirm we can build the graph with more than one iteration"""

    @ct.electron
    def half_quarter(n):
        return n / 2.0, n / 4.0

    @ct.lattice
    def add_half_quarter(a):
        half, quarter = half_quarter(a)
        return half + quarter

    add_half_quarter.build_graph(0.1)

    # Account for pp electron
    assert [0, 1, 2, 3, 4, 5, 6, 7, 8] == list(add_half_quarter.transport_graph._graph.nodes)


def test_wait_for():
    """Test whether wait_for functionality executes as expected"""

    @ct.electron
    def task_1a(a):
        return a**2

    @ct.electron
    def task_1b(a):
        return a**3

    @ct.electron
    def task_2(x, y):
        return x * y

    @ct.electron
    def task_3(b):
        return b**3

    @ct.lattice
    def workflow():
        res_1a = task_1a(2)
        res_1b = task_1b(2)
        res_2 = task_2(res_1a, 3)
        res_3 = ct.wait(task_3(5), [res_1a, res_1b])

        return task_2(res_2, res_3)

    dispatch_id = ct.dispatch(workflow)()
    result = ct.get_result(dispatch_id, wait=True)
    update.persist(result)

    assert result.status == Result.COMPLETED
    assert (
        result.get_node_result(node_id=6)["start_time"]
        > result.get_node_result(node_id=0)["end_time"]
    )
    assert (
        result.get_node_result(node_id=6)["start_time"]
        > result.get_node_result(node_id=2)["end_time"]
    )
    assert result.result == 1500
    rm._delete_result(dispatch_id)

    # Check that workflow function returns the same result when called directly

    assert workflow() == 1500


def test_electron_getitem():
    """Test electron __getitem__, both with raw keys and with electron keys"""

    @ct.electron
    def create_array():
        return [0, 1, 2, 3, 4, 5]

    @ct.electron
    def identity(x):
        return x

    @ct.lattice
    def workflow():
        arr = create_array()
        third_element = arr[2]
        return third_element

    @ct.lattice
    def workflow_using_electron_key():
        arr = create_array()
        third_element = arr[identity(2)]
        return third_element

    dispatch_id = ct.dispatch(workflow)()
    workflow_result = rm.get_result(dispatch_id, wait=True)
    assert workflow_result.result == 2
    rm._delete_result(dispatch_id)

    dispatch_id = ct.dispatch(workflow_using_electron_key)()
    workflow_result = rm.get_result(dispatch_id, wait=True)
    assert workflow_result.result == 2

    rm._delete_result(dispatch_id)


def test_electron_getattr():
    """Test electron __getattr__"""

    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    @ct.electron
    def create_point():
        return Point(3, 4)

    @ct.electron
    def echo(a):
        return a

    @ct.lattice
    def workflow():
        point = create_point()
        return point.x * point.x + point.y * point.y

    dispatch_id = ct.dispatch(workflow)()
    workflow_result = rm.get_result(dispatch_id, wait=True)
    assert workflow_result.result == 25
    rm._delete_result(dispatch_id)


def test_workflows_with_list_nodes():
    """Test workflows with auto generated list nodes"""

    @ct.electron
    def sum_array(arr):
        return sum(arr)

    @ct.electron
    def square(x):
        return x * x

    @ct.lattice
    def workflow(x):
        res_1 = sum_array(x)
        return square(res_1)

    dispatch_id = ct.dispatch(workflow)([1, 2, 3])

    res_obj = rm.get_result(dispatch_id, wait=True)

    assert res_obj.result == 36

    rm._delete_result(dispatch_id)


def test_workflows_with_dict_nodes():
    """Test workflows with auto generated dictionary nodes"""

    @ct.electron
    def sum_values(assoc_array):
        return sum(assoc_array.values())

    @ct.electron
    def square(x):
        return x * x

    @ct.lattice
    def workflow(x):
        res_1 = sum_values(x)
        return square(res_1)

    dispatch_id = ct.dispatch(workflow)({"x": 1, "y": 2, "z": 3})

    res_obj = rm.get_result(dispatch_id, wait=True)

    assert res_obj.result == 36

    rm._delete_result(dispatch_id)
