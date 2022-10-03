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

"""Testing results_dir migration script"""

import pickle
from pathlib import Path

from covalent._results_manager import Result
from covalent._shared_files.defaults import attr_prefix, generator_prefix, subscript_prefix
from covalent._workflow.transport import TransportableObject, _TransportGraph
from covalent_dispatcher._cli.migrate import (
    migrate_pickled_result_object,
    process_lattice,
    process_node,
    process_result_object,
    process_transport_graph,
    to_decoded_electron_collection,
)

dispatch_id = "652dc473-fa37-4846-85f3-b314204fd432"
sub_dispatch_id = "c333d0b3-8711-4595-9374-421f5482a592"

basedir = Path(__file__).parent
sample_results_dir = basedir / Path("sample_results_dir")
result_pkl = sample_results_dir / dispatch_id / "result.pkl"

# task node 0, parameter node 1
# attribute node 2
# sublattice node 3
# task node 4, generator nodes 5, 6
# subscript node 7


def get_sample_result_object():
    with open(result_pkl, "rb") as f:
        result_object = pickle.load(f)
    return result_object


def compare_nodes_and_edges(tg_orig: _TransportGraph, tg_new: _TransportGraph):
    """Convenience function for comparing a legacy transport graph with a processed one."""

    # Check metadata
    for n in tg_new._graph.nodes:
        metadata = tg_new._graph.nodes[n]["metadata"]
        assert "deps" in metadata
        assert "call_before" in metadata
        assert "call_after" in metadata

    # Check other node attributes
    task_node = tg_new._graph.nodes[0]
    orig_output = tg_orig._graph.nodes[0]["output"]

    assert isinstance(task_node["output"], TransportableObject)
    assert task_node["output"].get_deserialized().__dict__ == orig_output.__dict__

    collection_node = tg_new._graph.nodes[1]
    assert (
        collection_node["function"].get_serialized()
        == TransportableObject(to_decoded_electron_collection).get_serialized()
    )

    param_node = tg_new._graph.nodes[2]
    orig_output = tg_orig._graph.nodes[2]["output"]
    orig_value = tg_orig._graph.nodes[2]["value"]

    assert isinstance(param_node["output"], TransportableObject)
    assert isinstance(param_node["value"], TransportableObject)
    assert param_node["output"].get_deserialized() == orig_output

    param_node = tg_new._graph.nodes[3]
    orig_output = tg_orig._graph.nodes[3]["output"]
    orig_value = tg_orig._graph.nodes[3]["value"]

    assert isinstance(param_node["output"], TransportableObject)
    assert isinstance(param_node["value"], TransportableObject)
    assert param_node["output"].get_deserialized() == orig_output

    attr_node = tg_new._graph.nodes[4]
    orig_output = tg_orig._graph.nodes[4]["output"]

    assert isinstance(attr_node["output"], TransportableObject)
    assert attr_node["output"].get_deserialized() == orig_output
    assert "attribute_name" not in attr_node
    assert attr_prefix not in attr_node["name"]

    subl_node = tg_new._graph.nodes[5]
    orig_output = tg_orig._graph.nodes[5]["output"]

    assert isinstance(subl_node["output"], TransportableObject)
    assert isinstance(subl_node["sublattice_result"], Result)
    assert subl_node["output"].get_deserialized() == orig_output

    task_node = tg_new._graph.nodes[6]
    orig_output = tg_orig._graph.nodes[6]["output"]

    assert isinstance(task_node["output"], TransportableObject)
    assert task_node["output"].get_deserialized() == orig_output

    gen_node = tg_new._graph.nodes[7]
    orig_output = tg_orig._graph.nodes[7]["output"]

    assert isinstance(gen_node["output"], TransportableObject)
    assert gen_node["output"].get_deserialized() == orig_output
    assert "key" not in gen_node
    assert generator_prefix not in gen_node["name"]

    gen_node = tg_new._graph.nodes[8]
    orig_output = tg_orig._graph.nodes[8]["output"]

    assert isinstance(gen_node["output"], TransportableObject)
    assert gen_node["output"].get_deserialized() == orig_output
    assert "key" not in gen_node
    assert generator_prefix not in gen_node["name"]

    subscript_node = tg_new._graph.nodes[9]
    orig_output = tg_orig._graph.nodes[9]["output"]

    assert isinstance(subscript_node["output"], TransportableObject)
    assert subscript_node["output"].get_deserialized() == orig_output
    assert "key" not in subscript_node
    assert subscript_prefix not in subscript_node["name"]

    assert tg_orig._graph.edges == tg_new._graph.edges


def test_process_legacy_node():
    """Test process_node"""

    ro = get_sample_result_object()
    ro_orig = get_sample_result_object()
    tg = ro.lattice.transport_graph
    tg_orig = ro_orig.lattice.transport_graph

    task_node = tg._graph.nodes[0]
    orig_output = tg_orig._graph.nodes[0]["output"]
    process_node(task_node)

    param_node = tg._graph.nodes[2]
    orig_output = tg_orig._graph.nodes[2]["output"]
    orig_value = tg_orig._graph.nodes[2]["value"]
    process_node(param_node)

    param_node = tg._graph.nodes[3]
    orig_output = tg_orig._graph.nodes[3]["output"]
    orig_value = tg_orig._graph.nodes[3]["value"]
    process_node(param_node)

    attr_node = tg._graph.nodes[4]
    orig_output = tg_orig._graph.nodes[4]["output"]
    assert "attribute_name" in attr_node
    assert attr_prefix in attr_node["name"]
    process_node(attr_node)

    subl_node = tg._graph.nodes[5]
    orig_output = tg_orig._graph.nodes[5]["output"]
    assert "sublattice_result" in subl_node
    process_node(subl_node)

    task_node = tg._graph.nodes[6]
    orig_output = tg_orig._graph.nodes[6]["output"]
    process_node(task_node)

    gen_node = tg._graph.nodes[7]
    orig_output = tg_orig._graph.nodes[7]["output"]
    assert "key" in gen_node
    assert generator_prefix in gen_node["name"]
    process_node(gen_node)

    gen_node = tg._graph.nodes[8]
    orig_output = tg_orig._graph.nodes[8]["output"]
    assert "key" in gen_node
    assert generator_prefix in gen_node["name"]
    process_node(gen_node)

    subscript_node = tg._graph.nodes[9]
    orig_output = tg_orig._graph.nodes[9]["output"]
    assert "key" in subscript_node
    assert subscript_prefix in subscript_node["name"]
    process_node(subscript_node)


def test_process_transport_graph():
    """Test process_transport_graph"""

    ro = get_sample_result_object()

    tg = ro.lattice.transport_graph
    tg_new = process_transport_graph(tg)
    compare_nodes_and_edges(tg, tg_new)
    assert "dirty_nodes" in tg_new.__dict__


def test_process_transport_graph_is_idempotent():

    ro = get_sample_result_object()
    tg = ro.lattice.transport_graph
    tg_new = process_transport_graph(tg)
    compare_nodes_and_edges(tg, tg_new)

    tg_new_2 = process_transport_graph(tg_new)
    compare_nodes_and_edges(tg, tg_new_2)


def test_process_lattice():
    """Test process_lattice"""

    ro = get_sample_result_object()
    ro_orig = get_sample_result_object()
    lattice = process_lattice(ro._lattice)

    assert isinstance(lattice.workflow_function, TransportableObject)
    assert list(lattice.named_args.keys()) == ["z"]
    assert list(lattice.named_kwargs.keys()) == ["zz"]
    assert lattice.metadata["executor_data"]["short_name"] == "local"
    assert lattice.metadata["workflow_executor"] == "local"
    assert lattice.metadata["workflow_executor_data"] == {}
    assert lattice.metadata["deps"] == {}
    assert lattice.metadata["call_before"] == []
    assert lattice.metadata["call_after"] == []


2


def test_process_result_object():
    """Test process_result_object"""

    ro = get_sample_result_object()
    ro_new = process_result_object(ro)
    assert ro_new._inputs["args"] == ro_new.lattice.args
    assert ro_new._inputs["kwargs"] == ro_new.lattice.kwargs
    assert isinstance(ro_new._result, TransportableObject)
    assert "dirty_nodes" in ro_new.lattice.transport_graph.__dict__


def test_migrate_pickled_result_object(mocker):
    """Test migrate_pickled_result_object"""

    mock_process_ro = mocker.patch("covalent.utils.migrate.process_result_object")
    mock_persist = mocker.patch("covalent._results_manager.Result.persist")

    migrate_pickled_result_object(result_pkl)
    mock_process_ro.assert_called_once()
    mock_persist.assert_called_once()
