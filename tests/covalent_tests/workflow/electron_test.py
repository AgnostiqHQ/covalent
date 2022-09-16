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

from dataclasses import asdict

import covalent as ct
from covalent._shared_files.context_managers import active_lattice_manager
from covalent._shared_files.defaults import DefaultMetadataValues
from covalent._workflow.electron import Electron, to_decoded_electron_collection
from covalent._workflow.transport import TransportableObject, _TransportGraph, encode_metadata
from covalent.executor.executor_plugins.local import LocalExecutor

DEFAULT_METADATA_VALUES = asdict(DefaultMetadataValues())


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
        assert workflow.workflow_function.get_deserialized()() == 1500


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
        assert workflow_2.workflow_function.get_deserialized()() == 64


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
    metadata = encode_metadata(DEFAULT_METADATA_VALUES.copy())
    metadata["executor"] = "custom_executor"
    metadata["executor_data"] = {"attributes": {"instance_id": 1}}
    metadata["deps"] = {"pip": "pipdep", "bash": "bashdep"}
    node_id = e.add_collection_node_to_graph(tg, prefix=":", metadata=metadata)
    collection_fn = tg.get_node_value(node_id, "function").get_deserialized()

    collection = [
        TransportableObject.make_transportable(1),
        TransportableObject.make_transportable(2),
    ]

    collection_metadata = tg.get_node_value(node_id, "metadata")
    assert collection_metadata["deps"] == metadata["deps"]
    assert collection_metadata["executor"] == metadata["executor"]
    assert collection_metadata["executor_data"] == metadata["executor_data"]
    assert collection_metadata["call_before"] == metadata["call_before"]
    assert collection_metadata["call_before"] == metadata["call_after"]

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

    assert list(g.nodes) == [0, 1]
    assert list(g.edges) == [(1, 0, 0)]


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

    assert list(e_list_metadata["call_before"]) == []
    assert list(e_list_metadata["call_after"]) == []

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


def test_collection_node_executor_instance():
    """Test that collection nodes use the same executor instance as
    their main node."""

    @ct.electron(executor="local")
    def make_list(arr):
        return list(arr)

    @ct.electron(executor="local")
    def make_dict(mapping):
        return dict(mapping)

    @ct.lattice
    def list_workflow():
        return make_list([1, 2, 3])

    @ct.lattice
    def dict_workflow():
        return make_dict({"a": 1, "b": 2})

    list_workflow.build_graph()
    tg = list_workflow.transport_graph

    main_ex = tg.get_node_value(0, "metadata")["executor_data"]
    main_eid = main_ex["attributes"]["instance_id"]
    main_shared = main_ex["attributes"]["shared"]

    list_node_ex = tg.get_node_value(1, "metadata")["executor_data"]
    list_eid = list_node_ex["attributes"]["instance_id"]
    list_shared = list_node_ex["attributes"]["shared"]

    assert main_eid == list_eid
    assert main_shared is True
    assert list_shared is True

    dict_workflow.build_graph()
    tg = dict_workflow.transport_graph

    main_ex = tg.get_node_value(0, "metadata")["executor_data"]
    main_eid = main_ex["attributes"]["instance_id"]
    main_shared = main_ex["attributes"]["shared"]

    dict_node_ex = tg.get_node_value(1, "metadata")["executor_data"]
    dict_eid = dict_node_ex["attributes"]["instance_id"]
    dict_shared = dict_node_ex["attributes"]["shared"]

    assert main_eid == dict_eid
    assert main_shared is True
    assert dict_shared is True


def test_iter_node_executor_instance():
    """Test that generated nodes share the same executor instance as
    their main node."""

    @ct.electron(executor="local")
    def make_list(arr):
        return list(arr)

    @ct.lattice
    def unpacking_workflow():
        x, y, z = make_list([1, 2, 3])
        return x

    unpacking_workflow.build_graph()
    tg = unpacking_workflow.transport_graph

    main_ex = tg.get_node_value(0, "metadata")["executor_data"]
    main_shared = main_ex["attributes"]["shared"]
    main_eid = main_ex["attributes"]["instance_id"]

    # generated nodes are 5, 7, 9

    ex_x = tg.get_node_value(5, "metadata")["executor_data"]
    x_eid = ex_x["attributes"]["instance_id"]
    assert main_eid == x_eid
    assert main_shared is True
    assert main_ex == ex_x

    ex_y = tg.get_node_value(7, "metadata")["executor_data"]
    y_eid = ex_y["attributes"]["instance_id"]
    assert main_eid == y_eid
    assert main_ex == ex_y

    ex_z = tg.get_node_value(9, "metadata")["executor_data"]
    z_eid = ex_z["attributes"]["instance_id"]
    assert main_eid == z_eid
    assert main_ex == ex_z


def test_electron_getitem_executor_instance():
    """Test electron __getitem__ shares the main node's executor"""

    @ct.electron(executor="local")
    def create_array():
        return [0, 1, 2, 3, 4, 5]

    @ct.electron(executor="local")
    def identity(x):
        return x

    @ct.lattice
    def workflow():
        arr = create_array()
        third_element = arr[2]
        return third_element

    workflow.build_graph()
    tg = workflow.transport_graph
    main_ex = tg.get_node_value(0, "metadata")["executor_data"]
    main_shared = main_ex["attributes"]["shared"]
    main_eid = main_ex["attributes"]["instance_id"]

    getitem_ex = tg.get_node_value(1, "metadata")["executor_data"]
    getitem_eid = getitem_ex["attributes"]["instance_id"]

    assert main_shared is True
    assert main_eid == getitem_eid


def test_electron_getattr_executor_instance():
    """Test electron __getattr__ shares the main node's executor"""

    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    @ct.electron(executor="local")
    def create_point():
        return Point(3, 4)

    @ct.electron(executor="local")
    def echo(a):
        return a

    @ct.lattice
    def workflow():
        point = create_point()
        return point.x * point.x + point.y * point.y

    workflow.build_graph()
    tg = workflow.transport_graph
    main_ex = tg.get_node_value(0, "metadata")["executor_data"]
    main_shared = main_ex["attributes"]["shared"]
    main_eid = main_ex["attributes"]["instance_id"]

    getattr_ex = tg.get_node_value(1, "metadata")["executor_data"]
    getattr_eid = getattr_ex["attributes"]["instance_id"]

    assert main_shared is True
    assert main_eid == getattr_eid
