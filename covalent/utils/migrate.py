import covalent as ct
from covalent._results_manager import Result
from covalent._shared_files.defaults import (
    attr_prefix,
    electron_dict_prefix,
    electron_list_prefix,
    generator_prefix,
    parameter_prefix,
    prefix_separator,
    sublattice_prefix,
    subscript_prefix,
)
from covalent._shared_files.utils import get_named_params
from covalent._workflow.electron import to_decoded_electron_collection
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import TransportableObject, _TransportGraph, encode_metadata


def process_node(node: dict) -> dict:
    """Convert a node from a 0.110.2-vintage transport graph

    Args:
        node: dictionary of node attributes

    Returns:
        the converted node attributes
    """

    if "metadata" in node:
        node["metadata"] = encode_metadata(node["metadata"])

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

    lattice.transport_graph = process_transport_graph(lattice.transport_graph)
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

    return result_object
