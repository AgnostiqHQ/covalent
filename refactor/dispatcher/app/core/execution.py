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
Dummy methods for calls to the Runner API.
"""


def run_task(result_object: Result, task_id_batch: List[int], input_arg_batch: List[Dict]) -> bool:
    """Ask Runner to execute tasks - get back True (False) if resources are (not) available.

    The Runner might not have resources available to pick up the batch of tasks. In that case,
    this function continues to try running the tasks until the runner becomes free.
    """

    pass


def cancel_task(dispatch_id: int, task_id: int):
    """Cancel task execution."""

    pass


"""
Dummy method for calls to the UI API.
"""


def update_ui(result_object: Result):
    pass


"""
Status checking methods.
"""


def is_workflow_running(result_object: Result) -> bool:
    """Check if workflow is running."""

    return result_object.status == "RUNNING"


def is_workflow_completed(result_object: Result) -> bool:
    """Check if workflow is completed"""

    if result_object == Result.COMPLETED:
        return True
    elif result_object == Result.FAILED:
        return True
    else:
        task_id_batches = result_object.lattice.transport_graph.get_topologically_sorted_graph()

        for task_batch in task_id_batches:
            for node_id in task_batch:
                if (
                    result_object._get_node_status(node_id) == Result.FAILED
                    or Result.RUNNING
                    or Result.CANCELLED
                ):
                    return False

    # TODO - Ideally this setting of the status should happen elsewhere
    result_object.status = Result.COMPLETED
    return True


def is_task_completed(task_id: int, result_object: Result) -> bool:
    """Check if task is completed."""

    # TODO - Refactor `node_id` -> `task_id`
    # TODO - Clarify if FAILED status belongs here
    return result_object.get_node_status(task_id=task_id) == "COMPLETED" or "FAILED"


"""
Dispatcher functions.
"""


def cancel_workflow():
    """Cancel the workflow."""

    pass


def update_task_results(task_execution_result: Dict, result_object: Result):
    """Update the workflow with task execution results."""

    result_object._update_node(**task_execution_result)

    if is_workflow_completed(result_object=result_object):
        update_workflow_results(result_object=result_object)

    # TODO - Double check that this is fine. It's place holder for writing the result to the
    #  database.
    result_object.save()


def _post_process(lattice: Lattice, node_outputs: Dict, task_exec_order: List[List]):
    """TODO - Describe post processing here."""

    return "workflow_result"


def update_workflow_results(workflow_execution_result: Dict, result_object: Result):
    """Update workflow results"""

    # TODO - The logic to find the workflow_execution_result might need to go in here

    # TODO - This might be a very central component; consider in more detail
    order = result_object.lattice.transport_graph.get_topologically_sorted_graph()

    # post process the lattice
    result_object._result = _post_process(
        result_object.lattice, result_object.get_all_node_outputs(), order
    )

    result_object._status = Result.COMPLETED
    result_object._end_time = datetime.now(timezone.utc)

    # TODO - Double check that this is indeed equivalent to writing to the database
    result_object.save()

    # TODO - CHeck all the statuses and then run post process


def run_workflow():
    pass


def preprocess_tasks_before_execution(task_id_batch: list, result_object: Result):
    """Several things need to happen to the results object before the tasks can be sent for
    execution."""

    for task_id in task_id_batch:
        # Get name of the node for the current task
        node_name = result_object.lattice.transport_graph.get_node_value(task_id, "name")

        if node_name.startswith(
            (subscript_prefix, generator_prefix, parameter_prefix, attr_prefix)
        ):
            if node_name.startswith(parameter_prefix):
                output = result_object.lattice.transport_graph.get_node_value(task_id, "value")
            else:
                parent = result_object.lattice.transport_graph.get_dependencies(task_id)[0]
                output = result_object.lattice.transport_graph.get_node_value(parent, "output")

                if node_name.startswith(attr_prefix):
                    attr = result_object.lattice.transport_graph.get_node_value(
                        task_id, "attribute_name"
                    )
                    output = getattr(output, attr)
                else:
                    key = result_object.lattice.transport_graph.get_node_value(task_id, "key")
                    output = output[key]

            result_object._update_node(
                task_id,
                f"{node_name}({task_id})",
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
                Result.COMPLETED,
                output,
                None,
            )

        write_task_inputs(task_id, node_name, result_object)


def write_task_inputs(task_id, node_name, result_object):

    task_inputs = get_task_inputs(task_id, node_name, result_object)

    # TODO - write task inputs to the appropriate nodes in the transport graphs

    result_object.save()


def get_task_inputs(task_id: int, node_name: str, result_object: Result) -> Dict:
    """
    Return the required inputs for a task execution.
    This makes sure that any node with child nodes isn't executed twice and fetches the
    result of parent node to use as input for the child node.

    Args:
        task_id: Node id of this task in the transport graph.
        node_name: Name of the node.
        result_object: Result object to be used to update and store execution related
                       info including the results.

    Returns:
        inputs: Input dictionary to be passed to the task containing args, kwargs,
                and any parent node execution results if present.
    """

    if node_name.startswith(electron_list_prefix):
        values = [
            result_object.lattice.transport_graph.get_node_value(parent, "output")
            for parent in result_object.lattice.transport_graph.get_dependencies(task_id)
        ]
        task_input = {"args": [], "kwargs": {"x": values}}
    elif node_name.startswith(electron_dict_prefix):
        values = {}
        for parent in result_object.lattice.transport_graph.get_dependencies(task_id):
            key = result_object.lattice.transport_graph.get_edge_value(
                parent, task_id, "edge_name"
            )
            value = result_object.lattice.transport_graph.get_node_value(parent, "output")
            values[key] = value
        task_input = {"args": [], "kwargs": {"x": values}}
    else:
        task_input = {"args": [], "kwargs": {}}

        for parent in result_object.lattice.transport_graph.get_dependencies(task_id):

            param_type = result_object.lattice.transport_graph.get_edge_value(
                parent, task_id, "param_type"
            )

            value = result_object.lattice.transport_graph.get_node_value(parent, "output")

            if param_type == "arg":
                task_input["args"].append(value)

            elif param_type == "kwarg":
                key = result_object.lattice.transport_graph.get_edge_value(
                    parent, task_id, "edge_name"
                )

                task_input["kwargs"][key] = value
    return task_input


def dispatch_workflow(result_object: Result) -> None:
    """After a workflow has been popped from a queue (remember that dispatcher processes only
    one workflow at a time) and it has been validated, this function is run.

    If workflow is not running, i.e. just picked up from the queue, run dispatcher.
    """

    # This is the beginning of dispatch: result.status = Result.NEW_OBJ

    # TODO - Consider having a result_object.copy_transport_graph() method.
    # TODO - Consider creating a method to carry out the functionality below.
    transport_graph = _TransportGraph()
    transport_graph.deserialize(result_object.lattice.transport_graph)
    result_object._lattice.transport_graph = transport_graph
    result_object._initialize_nodes()

    result_object.save()  # Not sure what this does or why it's necessary. Assuming this is
    # writing the result object update to the database. We might not want to constantly read and
    # write.

    # Beginning the workflow execution process.
    result_object.status = Result.RUNNING
    task_schedule = result_object.lattice.transport_graph.get_topologically_sorted_graph()

    # TODO - Modify this logic so that it applies to sub-lattices as well
    while task_schedule:
        tasks = task_schedule.pop(0)
        preprocess_tasks_before_execution(task_id_batch=tasks, result_object=result_object)
        run_task(result_object=result_object, task_id_batch=tasks)

        # TODO - check that all the prerequisite tasks are completed before attempting the next
        #  batch of tasks.

    # TODO - After all the scheduled tasks have successfully been sent to the Runner API and the
    #  while loop above has completed, it doesn't mean that the workflow execution status is
    #  COMPLETED.

    if is_workflow_completed(result_object=result_object):
        # post process the lattice
        result_object._result = _post_process(
            result_object.lattice, result_object.get_all_node_outputs(), task_schedule
        )

        result_object._status = Result.COMPLETED
        result_object._end_time = datetime.now(timezone.utc)
        result_object.save(write_source=True)
