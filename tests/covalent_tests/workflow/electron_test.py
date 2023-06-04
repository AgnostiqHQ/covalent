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

"""Unit tests for electron"""

import json

import covalent as ct
from covalent._shared_files.context_managers import active_lattice_manager
from covalent._shared_files.defaults import sublattice_prefix
from covalent._workflow.electron import (
    Electron,
    _build_sublattice_graph,
    filter_null_metadata,
    get_serialized_function_str,
    to_decoded_electron_collection,
)
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import TransportableObject, _TransportGraph, encode_metadata
from covalent.executor.executor_plugins.local import LocalExecutor


@ct.electron
def task_1(a):
    import time

    time.sleep(3)
    return a**2


@ct.electron
def task_2(x, y):
    return x * y


@ct.electron
def task_3(b):
    return b**3


@ct.lattice
def workflow():
    res_1 = task_1(2)
    res_2 = task_2(res_1, 3)
    res_3 = ct.wait(task_3(5), res_1)

    return task_2(res_2, res_3)


@ct.lattice
def workflow_2():
    res_1 = task_1(2)
    res_2 = task_2(res_1, 3)
    res_3 = task_3(res_1)
    ct.wait(res_3, [res_1])

    return res_3


def test_build_sublattice_graph():
    """
    Test building a sublattice graph
    """

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    parent_metadata = {
        "executor": "parent_executor",
        "executor_data": {},
        "workflow_executor": "my_postprocessor",
        "workflow_executor_data": {},
        "deps": {"bash": None, "pip": None},
        "call_before": [],
        "call_after": [],
        "triggers": "mock-trigger",
        "results_dir": None,
    }

    json_lattice = _build_sublattice_graph(workflow, json.dumps(parent_metadata), 1)
    lattice = Lattice.deserialize_from_json(json_lattice)

    assert list(lattice.transport_graph._graph.nodes) == list(range(3))
    for k in lattice.metadata.keys():
        # results_dir will be deprecated soon
        if k == "triggers":
            assert lattice.metadata[k] is None
        elif k != "results_dir":
            assert parent_metadata[k] == lattice.metadata[k]


def test_wait_for_building():
    """Test to check whether the graph is built correctly with `wait_for`."""

    workflow.build_graph()
    assert workflow.transport_graph.get_edge_data(0, 4)[0]["wait_for"]
    assert workflow.transport_graph.get_edge_data(0, 4)[0]["edge_name"] == "!waiting_edge"


def test_wait_for_post_processing():
    """Test to check post processing with `wait` works fine."""

    workflow.build_graph()
    with active_lattice_manager.claim(workflow):
        workflow.post_processing = True
        workflow.electron_outputs = [
            (0, TransportableObject(4)),
            (2, TransportableObject(12)),
            (4, TransportableObject(125)),
            (6, TransportableObject(1500)),
        ]
        assert workflow.workflow_function.get_deserialized()()[1].get_deserialized() == 1500


def test_wait_for_post_processing_when_returning_waiting_electron():
    """Test to check post processing with `wait` works fine when returning
    an electron with incoming wait_for edges"""

    workflow_2.build_graph()
    with active_lattice_manager.claim(workflow_2):
        workflow_2.post_processing = True
        workflow_2.electron_outputs = [
            (0, TransportableObject(4)),
            (2, TransportableObject(12)),
            (4, TransportableObject(64)),
        ]
        assert workflow_2.workflow_function.get_deserialized()()[1].get_deserialized() == 64


def test_collection_node_helper_electron():
    """Unit test for `to_decoded_electron_collection`"""

    list_collection = [
        TransportableObject.make_transportable(1),
        TransportableObject.make_transportable(2),
    ]

    dict_collection = {"a": list_collection[0], "b": list_collection[1]}
    assert to_decoded_electron_collection(x=list_collection) == [1, 2]

    assert to_decoded_electron_collection(x=dict_collection) == {"a": 1, "b": 2}


def test_electron_add_collection_node():
    """Test `to_decoded_electron_collection` in `Electron.add_collection_node`"""

    def f(x):
        return x

    e = Electron(f)
    tg = _TransportGraph()
    node_id = e.add_collection_node_to_graph(tg, prefix=":")
    collection_fn = tg.get_node_value(node_id, "function").get_deserialized()

    collection = [
        TransportableObject.make_transportable(1),
        TransportableObject.make_transportable(2),
    ]

    assert collection_fn(x=collection) == [1, 2]


def test_injected_inputs_are_not_in_tg():
    """Test that arguments to electrons injected by calldeps aren't
    added to the transport graph"""

    def identity(y):
        return y

    calldep = ct.DepsCall(identity, args=[5], retval_keyword="y")

    @ct.electron(call_before=[calldep])
    def task(x, y=0):
        return (x, y)

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph(2)
    g = workflow.transport_graph._graph

    assert list(g.nodes) == list(range(3))
    assert list(g.edges) == [(0, 2, 0), (1, 0, 0)]


def test_metadata_in_electron_list():
    """Test if metadata of the created electron list apart from executor is set to default values"""

    def identity(y):
        return y

    calldep = ct.DepsCall(identity, args=[5], retval_keyword="y")

    @ct.electron(call_before=[calldep], executor=LocalExecutor())
    def task(x, y=0):
        return (x, y)

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph([2])

    task_metadata = workflow.transport_graph.get_node_value(0, "metadata")
    e_list_metadata = workflow.transport_graph.get_node_value(1, "metadata")

    assert not list(e_list_metadata["call_before"])
    assert not list(e_list_metadata["call_after"])

    assert e_list_metadata["executor"] == task_metadata["executor"]


def test_electron_metadata_is_serialized_early():
    """Test that electron metadata is JSON-serialized before it is
    stored in the graph.

    This checks that `constraints` are already serialized before being
    passed to the `decorator_electron` closure.

    """

    def identity(y):
        return y

    calldep = ct.DepsCall(identity, args=[5], retval_keyword="y")

    @ct.electron(call_before=[calldep], executor=LocalExecutor())
    def task(x):
        return x

    @ct.lattice(workflow_executor=LocalExecutor())
    def workflow(x):
        return task(x)

    workflow.build_graph(2)
    node_0_metadata = workflow.transport_graph.get_node_value(0, "metadata")
    assert node_0_metadata == encode_metadata(node_0_metadata)
    node_1_metadata = workflow.transport_graph.get_node_value(1, "metadata")
    assert node_1_metadata == encode_metadata(node_1_metadata)


def test_autogen_list_electrons():
    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph([5, 7])

    g = workflow.transport_graph._graph

    assert list(g.nodes) == list(range(5))
    fn = g.nodes[1]["function"].get_deserialized()
    assert fn(2, 5, 7) == [2, 5, 7]

    assert g.nodes[2]["value"].get_deserialized() == 5
    assert g.nodes[3]["value"].get_deserialized() == 7
    assert set(g.edges) == {(1, 0, 0), (3, 1, 0), (2, 1, 0), (0, 4, 0)}


def test_autogen_dict_electrons():
    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph({"x": 5, "y": 7})

    g = workflow.transport_graph._graph

    assert list(g.nodes) == list(range(5))
    fn = g.nodes[1]["function"].get_deserialized()
    assert fn(x=2, y=5, z=7) == {"x": 2, "y": 5, "z": 7}
    assert g.nodes[2]["value"].get_deserialized() == 5
    assert g.nodes[3]["value"].get_deserialized() == 7
    assert set(g.edges) == {(1, 0, 0), (3, 1, 0), (2, 1, 0), (0, 4, 0)}


def test_as_transportable_dict():
    """Test the get transportable electron function."""

    @ct.electron
    def test_func(a):
        return a

    mock_metadata = {"a": 1, "b": 2, "c": None}
    # Construct bound electron, i.e. electron with non-null function and node_id
    electron = Electron(function=test_func, node_id=1, metadata=mock_metadata)
    transportable_electron = electron.as_transportable_dict

    assert transportable_electron["name"] == "test_func"
    assert transportable_electron["metadata"] == filter_null_metadata(mock_metadata)
    assert transportable_electron["function_string"] == get_serialized_function_str(test_func)
    assert TransportableObject(test_func).to_dict() == transportable_electron["function"]


def test_call_sublattice():
    """Test the sublattice logic when the __call__ method is invoked."""

    @ct.lattice(executor="mock")
    def mock_workflow(x):
        return sublattice(x)

    @ct.electron
    def mock_task(x):
        return x

    @ct.electron
    @ct.lattice
    def sublattice(x):
        return mock_task(x)

    with active_lattice_manager.claim(mock_workflow):
        bound_electron = sublattice()
        assert bound_electron.metadata["executor"] == "mock"
        for _, node_data in mock_workflow.transport_graph._graph.nodes(data=True):
            if node_data["name"].startswith(sublattice_prefix):
                assert "mock_task" in node_data["function_string"]
                assert "sublattice" in node_data["function_string"]
                assert (
                    node_data["function"].get_deserialized().__name__ == "_build_sublattice_graph"
                )


def test_electron_auto_task_groups():
    @ct.electron
    def task(arr: list):
        return sum(arr)

    @ct.electron
    @ct.lattice
    def sublattice(x):
        return task(x)

    @ct.lattice
    def workflow(x):
        return sublattice(x)

    workflow.build_graph([[1, 2], 3])
    tg = workflow.transport_graph
    assert all(tg.get_node_value(i, "task_group_id") == 0 for i in [0, 3, 4])
    assert all(tg.get_node_value(i, "task_group_id") == i for i in [1, 2, 5, 6, 7, 8])


def test_electron_get_attr():
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    @ct.electron
    def create_point():
        return Point(3, 4)

    @ct.electron
    def add(a, b):
        return a + b

    @ct.lattice
    def workflow():
        point = create_point()
        return add(point.x, point.y)

    workflow.build_graph()
    tg = workflow.transport_graph

    # TG:
    # 0: point
    # 1: point.__getattr__
    # 2: "x"
    # 3: point.__getattr__
    # 4: "y"
    # 5: add
    # 6: "postprocess"

    point_electron_gid = tg.get_node_value(0, "task_group_id")
    getitem_x_gid = tg.get_node_value(1, "task_group_id")
    getitem_y_gid = tg.get_node_value(3, "task_group_id")
    assert point_electron_gid == 0
    assert getitem_x_gid == point_electron_gid
    assert getitem_y_gid == point_electron_gid
    assert all(tg.get_node_value(i, "task_group_id") == i for i in [2, 4, 5, 6])


def test_electron_auto_task_groups_getitem():
    """Test task packing with __getitem__"""

    @ct.electron
    def create_array():
        return [3, 4]

    @ct.electron
    def add(a, b):
        return a + b

    @ct.lattice
    def workflow():
        arr = create_array()
        return add(arr[0], arr[1])

    workflow.build_graph()
    tg = workflow.transport_graph

    # TG:
    # 0: arr
    # 1: arr.__getitem__
    # 2: 0
    # 3: arr.__getitem__
    # 4: 1
    # 5: add
    # 6: "postprocess"

    arr_electron_gid = tg.get_node_value(0, "task_group_id")
    getitem_x_gid = tg.get_node_value(1, "task_group_id")
    getitem_y_gid = tg.get_node_value(3, "task_group_id")
    assert arr_electron_gid == 0
    assert getitem_x_gid == arr_electron_gid
    assert getitem_y_gid == arr_electron_gid
    assert all(tg.get_node_value(i, "task_group_id") == i for i in [2, 4, 5, 6])


def test_electron_auto_task_groups_iter():
    """Test task packing with __iter__"""

    @ct.electron
    def create_tuple():
        return (3, 4)

    @ct.electron
    def add(a, b):
        return a + b

    @ct.lattice
    def workflow():
        tup = create_tuple()
        x, y = tup
        return add(x, y)

    workflow.build_graph()
    tg = workflow.transport_graph

    # TG:
    # 0: tup
    # 1: tup.__getitem__
    # 2: 0
    # 3: tup.__getitem__
    # 4: 1
    # 5: add
    # 6: "postprocess"

    tup_electron_gid = tg.get_node_value(0, "task_group_id")
    getitem_x_gid = tg.get_node_value(1, "task_group_id")
    getitem_y_gid = tg.get_node_value(3, "task_group_id")
    assert tup_electron_gid == 0
    assert getitem_x_gid == tup_electron_gid
    assert getitem_y_gid == tup_electron_gid
    assert all(tg.get_node_value(i, "task_group_id") == i for i in [2, 4, 5, 6])


def test_electron_executor_property():
    """
    Test that the executor property assignment
    of an electron works as expected.
    """

    @ct.electron
    def mock_task():
        pass

    mock_encoded_metadata = encode_metadata({"executor": LocalExecutor()})

    mock_task_electron = mock_task.electron_object

    # If string is passed
    mock_task_electron.executor = "mock"
    assert mock_task_electron.metadata["executor"] == "mock"

    # If executor object is passed
    mock_task_electron.executor = LocalExecutor()
    assert mock_task_electron.metadata["executor"] == mock_encoded_metadata["executor"]
    assert mock_task_electron.metadata["executor_data"] == mock_encoded_metadata["executor_data"]
