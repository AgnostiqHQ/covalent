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

"""Utility functions for the Dispatcher microservice."""

from datetime import datetime, timezone
from typing import Any, Dict, List

from covalent._results_manager import Result
from covalent._shared_files.context_managers import active_lattice_manager
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
from covalent._workflow.lattice import Lattice


def preprocess_transport_graph(task_id: int, task_name: str, result_obj: Result) -> Result:
    """Ensure that the execution status of the task nodes in the transport graph are initialized
    properly."""

    is_executable_node = True

    if task_name.startswith((subscript_prefix, generator_prefix, parameter_prefix, attr_prefix)):
        if task_name.startswith(parameter_prefix):
            output = result_obj.lattice.transport_graph.get_node_value(task_id, "value")
        else:
            parent = result_obj.lattice.transport_graph.get_dependencies(task_id)[0]
            output = result_obj.lattice.transport_graph.get_node_value(parent, "output")

            if task_name.startswith(attr_prefix):
                attr = result_obj.lattice.transport_graph.get_node_value(task_id, "attribute_name")
                output = getattr(output, attr)
            else:
                key = result_obj.lattice.transport_graph.get_node_value(task_id, "key")
                output = output[key]

        result_obj._update_node(
            node_id=task_id,
            node_name=f"{task_name}({task_id})",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            status=Result.COMPLETED,
            output=output,
        )

        is_executable_node = False

    return result_obj, is_executable_node


def _post_process(lattice: Lattice, task_outputs: Dict) -> Any:
    """
    Post processing function to be called after the lattice execution.
    This takes care of executing statements that were not an electron
    but were inside the lattice's function. It also replaces any calls
    to an electron with the result of that electron execution, hence
    preventing a local execution of electron's function.

    Note: Here `node_outputs` is used instead of `electron_outputs`
    since an electron can be called multiple times with possibly different
    arguments, but every time it's called, it will be executed as a separate node.
    Thus, output of every node is used.

    Args:
        lattice: Lattice object that was dispatched.
        task_outputs: Dictionary containing the output of all the tasks.

    Returns:
        result: The result of the lattice function.
    """

    ordered_task_outputs = [
        val
        for key, val in task_outputs.items()
        if not key.startswith(prefix_separator) or key.startswith(sublattice_prefix)
    ]

    with active_lattice_manager.claim(lattice):
        lattice.post_processing = True
        lattice.electron_outputs = ordered_task_outputs
        result = lattice.workflow_function(*lattice.args, **lattice.kwargs)
        lattice.post_processing = False
        return result


def get_task_inputs(task_id: int, node_name: str, result_obj: Result) -> Dict:
    """
    Return the required inputs for a task execution.
    This makes sure that any node with child nodes isn't executed twice and fetches the
    result of parent node to use as input for the child node.

    Args:
        task_id: Node id of this task in the transport graph.
        node_name: Name of the node.
        result_obj: Result object to be used to update and store execution related
                       info including the results.

    Returns:
        inputs: Input dictionary to be passed to the task containing args, kwargs,
                and any parent node execution results if present.
    """

    if node_name.startswith(electron_list_prefix):
        values = [
            result_obj.lattice.transport_graph.get_node_value(parent, "output")
            for parent in result_obj.lattice.transport_graph.get_dependencies(task_id)
        ]
        task_inputs = {"args": [], "kwargs": {"x": values}}
    elif node_name.startswith(electron_dict_prefix):
        values = {}
        for parent in result_obj.lattice.transport_graph.get_dependencies(task_id):
            key = result_obj.lattice.transport_graph.get_edge_value(parent, task_id, "edge_name")
            value = result_obj.lattice.transport_graph.get_node_value(parent, "output")
            values[key] = value
        task_inputs = {"args": [], "kwargs": {"x": values}}
    else:
        task_inputs = {"args": [], "kwargs": {}}

        for parent in result_obj.lattice.transport_graph.get_dependencies(task_id):

            param_type = result_obj.lattice.transport_graph.get_edge_value(
                parent, task_id, "param_type"
            )

            value = result_obj.lattice.transport_graph.get_node_value(parent, "output")

            if param_type == "arg":
                task_inputs["args"].append(value)

            elif param_type == "kwarg":
                key = result_obj.lattice.transport_graph.get_edge_value(
                    parent, task_id, "edge_name"
                )

                task_inputs["kwargs"][key] = value
    return task_inputs


def is_sublattice(task_name: str = None) -> bool:
    """Check if the transport graph task node is a sublattice. When the workflow is first
    dispatched, the build graph step is responsible for attaching a `sublattice` prefix to the
    corresponding task node."""

    return task_name.startswith(sublattice_prefix)


def are_tasks_running(result_obj: Result) -> bool:
    """Check if any of the tasks are still running. A task is considered not `running` if it was completed, failed or cancelled."""

    return all(
        result_obj._get_node_status(task_id) in [Result.RUNNING, Result.NEW_OBJ]
        for task_id in range(result_obj._num_nodes)
    )


def get_task_order(result_obj: Result) -> List[List]:
    """Find the order in which the tasks need to be executed. At the current moment this is
    based simply on the topologically sorted task nodes in the graph. In the future,
    this function can become much more sophisticated and optimized.
    """

    return result_obj.lattice.transport_graph.get_topologically_sorted_graph()
