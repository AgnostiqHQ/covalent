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

from datetime import datetime, timezone
from typing import Dict, List

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
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import _TransportGraph

"""
Main functions:
    - dispatch workflow
    - update workflow
    - cancel workflow
"""


def dispatch_workflow(result_obj: Result) -> Result:
    """Main dispatch function. Responsible for starting off the workflow dispatch."""

    if result_obj.status == Result.NEW_OBJ:
        result_obj = init_result_pre_dispatch(result_obj=result_obj)
        result_obj._status = Result.RUNNING

    task_schedule = result_obj.lattice.transport_graph.get_topologically_sorted_graph()
    result_obj = dispatch_tasks(task_schedule=task_schedule, result_obj=result_obj)

    return result_obj


def update_workflow(result_obj: Result) -> Result:
    """Main update function. Called by the Runner API when there is an update for task
    execution status."""

    pass


def cancel_workflow():
    """Main cancel function. Called by the user via ct.cancel(dispatch_id)."""

    pass


def init_result_pre_dispatch(result_obj: Result):
    transport_graph = _TransportGraph()
    transport_graph.deserialize(result_obj.lattice.transport_graph)
    result_obj._lattice.transport_graph = transport_graph
    result_obj._initialize_nodes()
    return result_obj


def dispatch_tasks(task_schedule: List[List], result_obj: Result) -> Result:
    """Responsible for preprocessing the tasks, and sending the tasks for execution to the
    Runner API in batches."""

    while task_schedule:
        tasks = task_schedule.pop(0)
        input_args = []

        for task_id in tasks:
            if is_sublattice(task_id=task_id):
                sublattice_task_schedule = get_sublattice_task_schedule(task_id=task_id)
                dispatch_tasks(task_schedule=sublattice_task_schedule, result_obj=result_obj)

            else:
                task_name = result_obj.lattice.transport_graph.get_node_value(task_id, "name")
                preprocess_transport_graph(
                    task_id=task_id, task_name=task_name, result_obj=result_obj
                )
                input_args.append(
                    get_task_inputs(task_id=task_id, node_name=task_name, result_obj=result_obj)
                )

        run_task(result_obj=result_obj, task_id_batch=tasks, input_arg_batch=input_args)

    return result_obj


def preprocess_transport_graph(task_id: int, task_name: str, result_obj: Result) -> Result:
    """Ensure that the execution status of the task nodes in the transport graph are initialized
    properly."""

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
            task_id,
            f"{task_name}({task_id})",
            datetime.now(timezone.utc),
            datetime.now(timezone.utc),
            Result.COMPLETED,
            output,
            None,
        )
    return result_obj


def is_sublattice(task_id: int) -> bool:
    # TODO - Find out if task is sublattice.

    return True


def get_sublattice_task_schedule(task_id: int) -> List[List]:
    # TODO - Get sublattice task schedule.

    pass


def run_task(result_obj: Result, task_id_batch: List[int], input_arg_batch: List[Dict]):
    """Ask Runner to execute tasks - get back True (False) if resources are (not) available.

    The Runner might not have resources available to pick up the batch of tasks. In that case,
    this function continues to try running the tasks until the runner becomes free.
    """

    pass


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
        task_input = {"args": [], "kwargs": {"x": values}}
    elif node_name.startswith(electron_dict_prefix):
        values = {}
        for parent in result_obj.lattice.transport_graph.get_dependencies(task_id):
            key = result_obj.lattice.transport_graph.get_edge_value(parent, task_id, "edge_name")
            value = result_obj.lattice.transport_graph.get_node_value(parent, "output")
            values[key] = value
        task_input = {"args": [], "kwargs": {"x": values}}
    else:
        task_input = {"args": [], "kwargs": {}}

        for parent in result_obj.lattice.transport_graph.get_dependencies(task_id):

            param_type = result_obj.lattice.transport_graph.get_edge_value(
                parent, task_id, "param_type"
            )

            value = result_obj.lattice.transport_graph.get_node_value(parent, "output")

            if param_type == "arg":
                task_input["args"].append(value)

            elif param_type == "kwarg":
                key = result_obj.lattice.transport_graph.get_edge_value(
                    parent, task_id, "edge_name"
                )

                task_input["kwargs"][key] = value
    return task_input
