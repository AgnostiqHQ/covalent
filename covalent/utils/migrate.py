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

"""Utils for migrating legacy (0.110-era) result object to a modern result object."""

import pickle

from .._results_manager import Result
from .._shared_files.defaults import (
    attr_prefix,
    electron_dict_prefix,
    electron_list_prefix,
    generator_prefix,
    parameter_prefix,
    subscript_prefix,
)
from .._shared_files.utils import get_named_params
from .._workflow.electron import to_decoded_electron_collection
from .._workflow.lattice import Lattice
from .._workflow.transport import TransportableObject, _TransportGraph, encode_metadata


def process_node(node: dict) -> dict:
    """Convert a node from a 0.110.2-vintage transport graph

    Args:
        node: dictionary of node attributes

    Returns:
        the converted node attributes
    """

    if "metadata" in node:
        node["metadata"] = encode_metadata(node["metadata"])
        if "deps" not in node["metadata"]:
            node["metadata"]["deps"] = {}
        if "call_before" not in node["metadata"]:
            node["metadata"]["call_before"] = []
        if "call_after" not in node["metadata"]:
            node["metadata"]["call_after"] = []

    node_name = node["name"]

    # encode output, remove "attribute_name", strip "attr_prefix" from name
    if node_name.startswith(attr_prefix):
        node["output"] = TransportableObject.make_transportable(node["output"])
        if "attribute_name" in node:
            del node["attribute_name"]
        new_node_name = node_name.replace(attr_prefix, "")
        node["name"] = new_node_name

    # encode output, remove "key", strip "generator_prefix" from name
    elif node_name.startswith(generator_prefix):
        node["output"] = TransportableObject.make_transportable(node["output"])
        if "key" in node:
            del node["key"]
        new_node_name = node_name.replace(generator_prefix, "")
        node["name"] = new_node_name

    # encode output, remove "key", strip "subscript_prefix" from name
    elif node_name.startswith(subscript_prefix):
        node["output"] = TransportableObject.make_transportable(node["output"])
        if "key" in node:
            del node["key"]
        new_node_name = node_name.replace(subscript_prefix, "")
        node["name"] = new_node_name

    # Replace function for collection nodes
    elif node_name.startswith(electron_list_prefix) or node_name.startswith(electron_dict_prefix):
        node["function"] = TransportableObject(to_decoded_electron_collection)

    # Encode "value" and "output" for parameter nodes
    elif node_name.startswith(parameter_prefix):
        node["value"] = TransportableObject.make_transportable(node["value"])
        node["output"] = TransportableObject.make_transportable(node["output"])

    # Function nodes: encode output and sublattice_result
    else:
        node["output"] = TransportableObject.make_transportable(node["output"])
        if "sublattice_result" in node:
            if node["sublattice_result"] is not None:
                node["sublattice_result"] = process_result_object(node["sublattice_result"])

    return node


def process_transport_graph(tg: _TransportGraph) -> _TransportGraph:
    """Convert a 0.110.2-vintage transport graph to a modern transport graph

    Args:
        tg: old Transport Graph

    Returns:
        the modernized Transport Graph
    """
    tg_new = _TransportGraph()
    g = tg.get_internal_graph_copy()
    for node_id in g.nodes:
        print(f"Processing node {node_id}")
        process_node(g.nodes[node_id])

    if tg.lattice_metadata:
        tg.lattice_metadata = encode_metadata(tg.lattice_metadata)

    tg_new._graph = g
    return tg_new


def process_lattice(lattice: Lattice) -> Lattice:
    """Convert a "legacy" (0.110.2) Lattice to a modern Lattice

    Args:
        lattice: old lattice

    Returns:
        the modernized lattice
    """

    workflow_function = lattice.workflow_function
    lattice.workflow_function = TransportableObject.make_transportable(workflow_function)
    args = [TransportableObject.make_transportable(arg) for arg in lattice.args]
    kwargs = {k: TransportableObject.make_transportable(v) for k, v in lattice.kwargs.items()}
    lattice.args = args
    lattice.kwargs = kwargs

    workflow_function = lattice.workflow_function.get_deserialized()

    named_args, named_kwargs = get_named_params(workflow_function, lattice.args, lattice.kwargs)
    lattice.named_args = named_args
    lattice.named_kwargs = named_kwargs

    metadata = lattice.metadata

    if "workflow_executor" not in metadata:
        metadata["workflow_executor"] = "local"

    metadata = encode_metadata(metadata)
    lattice.metadata = metadata
    lattice.metadata["deps"] = {}
    lattice.metadata["call_before"] = []
    lattice.metadata["call_after"] = []

    lattice.transport_graph = process_transport_graph(lattice.transport_graph)
    lattice.transport_graph.lattice_metadata = lattice.metadata
    print("Processed transport graph")

    return lattice


def process_result_object(result_object: Result) -> Result:
    """Convert a "legacy" (0.110.2) Result object to a modern Result object

    Args:
        result_object: the old Result object

    Returns:
        the modernized result object
    """

    print(f"Processing result object for dispatch {result_object.dispatch_id}")
    process_lattice(result_object._lattice)
    print("Processed lattice")
    if result_object.lattice.args:
        result_object._inputs["args"] = result_object.lattice.args
    if result_object.lattice.kwargs:
        result_object._inputs["kwargs"] = result_object.lattice.kwargs

    result_object._result = TransportableObject.make_transportable(result_object._result)
    tg = result_object.lattice.transport_graph
    for n in tg._graph.nodes:
        tg.dirty_nodes.append(n)

    return result_object


def migrate_pickled_result_object(path: str) -> None:
    """Save legacy (0.110.2) result pickle file to a DataStore.

    This first transforms certain legacy properties of the result
    object and then persists the result object to the datastore.

    Args:
        path: path of the `result.pkl` file
    """

    with open(path, "rb") as f:
        result_object = pickle.load(f)

    process_result_object(result_object)
    result_object.persist()
