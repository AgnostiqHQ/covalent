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

import covalent as ct
from covalent._shared_files.context_managers import active_lattice_manager
from covalent._workflow.electron import Electron
from covalent._workflow.transport import TransportableObject, _TransportGraph

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
    res_3 = task_3(5).wait_for(res_1)

    return task_2(res_2, res_3)


def test_wait_for_building():
    """Test to check whether the graph is built correctly with `wait_for`."""

    workflow.build_graph()
    assert workflow.transport_graph.get_edge_data(0, 4)[0]["wait_for"]
    assert workflow.transport_graph.get_edge_data(0, 4)[0]["edge_name"] == "!waiting_edge"


def test_wait_for_post_processing():
    """Test to check post processing with `wait_for` works fine."""

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

    assert list(g.nodes) == [0, 1]
    assert list(g.edges) == [(1, 0, 0)]



def test_metadata_in_electron_list():
    """Test if metadata of the created electron list apart from executor is set to default values"""


    def identity(y):
        return y

    calldep = ct.DepsCall(identity, args=[5], retval_keyword="y")

    @ct.electron(call_before=[calldep],executor=LocalExecutor())
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
