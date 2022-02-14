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

"""
Defines the core functionality of the dispatcher
"""

import traceback
from datetime import datetime, timezone
from typing import Any, Coroutine, Dict, List

import cloudpickle as pickle
import dask
from dask.distributed import Client, Variable

from covalent import dispatch_sync
from covalent._results_manager import Result
from covalent._results_manager import results_manager as rm
from covalent._shared_files import logger
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
from covalent._shared_files.util_classes import TaskExecutionMetadata
from covalent._workflow.lattice import Lattice
from covalent.executor import _executor_manager
from covalent_ui import result_webhook

app_log = logger.app_log
log_stack_info = logger.log_stack_info

dask_client = Client(processes=False, dashboard_address=":0")


def _get_task_inputs(
    task_input: dict, node_id: int, node_name: str, result_object: Result
) -> dict:
    """
    Return the required inputs for a task execution.
    This makes sure that any node with child nodes isn't executed twice and fetches the
    result of parent node to use as input for the child node.

    Args:
        task_input: Input dictionary for the task containing the kwargs
                    assigned to its function.
        node_id: Node id of this task in the transport graph.
        node_name: Name of the node.
        result_object: Result object to be used to update and store execution related
                       info including the results.

    Returns:
        inputs: Input dictionary to be passed to the task containing kwargs
                and any parent node execution results if present.
    """

    if node_name.startswith(electron_list_prefix):
        values = [
            result_object.lattice.transport_graph.get_node_value(parent, "output")
            for parent in result_object.lattice.transport_graph.get_dependencies(node_id)
        ]
        task_input = {"x": values}
    elif node_name.startswith(electron_dict_prefix):
        values = {}
        for parent in result_object.lattice.transport_graph.get_dependencies(node_id):
            key = result_object.lattice.transport_graph.get_edge_value(parent, node_id, "variable")
            value = result_object.lattice.transport_graph.get_node_value(parent, "output")
            values[key] = value
        task_input = {"x": values}
    else:
        for parent in result_object.lattice.transport_graph.get_dependencies(node_id):
            key = result_object.lattice.transport_graph.get_edge_value(parent, node_id, "variable")
            value = result_object.lattice.transport_graph.get_node_value(parent, "output")
            task_input[key] = value
    return task_input


def _post_process(lattice: Lattice, node_outputs: Dict, execution_order: List[List]) -> Any:
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
        node_outputs: Dictionary containing the output of all the nodes.
        execution_order: List of lists containing the order of execution of the nodes.

    Reurns:
        result: The result of the lattice function.
    """

    keys_of_outputs = list(node_outputs.keys())
    values_of_outputs = list(node_outputs.values())

    ordered_node_outputs = []
    for node_id_list in execution_order:
        for node_id in node_id_list:
            # Here we only need outputs of nodes which are executable
            if not keys_of_outputs[node_id].startswith(prefix_separator) or keys_of_outputs[
                node_id
            ].startswith(sublattice_prefix):
                ordered_node_outputs.append(values_of_outputs[node_id])

    with active_lattice_manager.claim(lattice):
        lattice.post_processing = True
        lattice.electron_outputs = ordered_node_outputs
        result = lattice.workflow_function(**lattice.kwargs)
        lattice.post_processing = False
        return result


def _run_task(
    inputs: Dict,
    result_object: Result,
    node_id: int,
) -> None:
    """
    Run a task with given inputs on the selected backend.
    Also updates the status of current node execution while
    checking if a redispatch has occurred. Exclude those nodes
    from execution which were completed.

    Also verifies if execution of this dispatch has been cancelled.

    Args:
        inputs: Inputs for the task.
        result_object: Result object being used for current dispatch
        node_id: Node id of the task to be executed.

    Returns:
        None
    """

    serialized_callable = result_object.lattice.transport_graph.get_node_value(node_id, "function")
    task_md = result_object.lattice.transport_graph.get_node_value(node_id, "exec_plan")
    node_name = (
        result_object.lattice.transport_graph.get_node_value(node_id, "name") + f"({node_id})"
    )

    shared_var = Variable(result_object.dispatch_id, client=dask_client)
    if shared_var.get() == str(Result.CANCELLED):
        app_log.info("Cancellation requested for dispatch %s", result_object.dispatch_id)

        result_object._update_node(
            node_id,
            node_name,
            None,
            None,
            Result.CANCELLED,
            None,
            None,
        )

        result_object.save()
        result_webhook.send_update(result_object)

        return

    if result_object._get_node_status(node_id) == Result.COMPLETED:
        return

    # the executor is determined during scheduling and provided in the execution metadata
    executor = _executor_manager.get_executor(task_md.selected_executor)

    # run the task on the executor and register any failures
    try:
        start_time = datetime.now(timezone.utc)
        result_object._update_node(
            node_id, node_name, start_time, None, Result.RUNNING, None, None
        )
        result_object.save()
        result_webhook.send_update(result_object)

        if node_name.startswith(sublattice_prefix):
            func = serialized_callable.get_deserialized()
            sublattice_result = dispatch_sync(func)(**inputs)
            output = sublattice_result.result

            end_time = datetime.now(timezone.utc)

            result_object._update_node(
                node_id,
                node_name,
                start_time,
                end_time,
                Result.COMPLETED,
                output,
                None,
                sublattice_result,
            )

        else:
            output, stdout, stderr = executor.execute(
                serialized_callable,
                inputs,
                task_md.execution_args,
                result_object.dispatch_id,
                node_id,
            )

            end_time = datetime.now(timezone.utc)

            result_object._update_node(
                node_id,
                node_name,
                start_time,
                end_time,
                Result.COMPLETED,
                output,
                None,
                stdout=stdout,
                stderr=stderr,
            )

    except Exception as ex:
        end_time = datetime.now(timezone.utc)
        result_object._update_node(
            node_id,
            node_name,
            start_time,
            end_time,
            Result.FAILED,
            None,
            "".join(traceback.TracebackException.from_exception(ex).format()),
        )

    result_object.save()
    result_webhook.send_update(result_object)


def _run_planned_workflow(result_object: Result) -> Result:
    """
    Run the workflow in the topological order of their position on the
    transport graph. Does this in an asynchronous manner so that nodes
    at the same level are executed in parallel. Also updates the status
    of the whole workflow execution.

    Args:
        result_object: Result object being used for current dispatch

    Returns:
        None
    """

    shared_var = Variable(result_object.dispatch_id, client=dask_client)
    shared_var.set(str(Result.RUNNING))

    result_object._status = Result.RUNNING
    result_object._start_time = datetime.now(timezone.utc)

    order = result_object.lattice.transport_graph.get_topologically_sorted_graph()

    for nodes in order:
        tasks: List[Coroutine] = []

        for node_id in nodes:
            # Get all inputs for the current task
            task_input = result_object.lattice.transport_graph.get_node_value(node_id, "kwargs")
            node_name = result_object.lattice.transport_graph.get_node_value(node_id, "name")

            if node_name.startswith(
                (subscript_prefix, generator_prefix, parameter_prefix, attr_prefix)
            ):
                if node_name.startswith(parameter_prefix):
                    output = list(task_input.values())[0]
                else:
                    parent = result_object.lattice.transport_graph.get_dependencies(node_id)[0]
                    output = result_object.lattice.transport_graph.get_node_value(parent, "output")

                    if node_name.startswith(attr_prefix):
                        attr = task_input["attr"]
                        output = getattr(output, attr)
                    else:
                        key = task_input["key"]
                        output = output[key]

                result_object._update_node(
                    node_id,
                    node_name + f"({node_id})",
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc),
                    Result.COMPLETED,
                    output,
                    None,
                )
                continue

            task_input = _get_task_inputs(task_input, node_id, node_name, result_object)

            # Add the task generated for the node to the list of tasks
            tasks.append(dask.delayed(_run_task)(task_input, result_object, node_id))

        # run the tasks for the current iteration in parallel
        dask.compute(*tasks)

        # When one or more nodes failed in the last iteration, don't iterate further
        for node_id in nodes:
            if result_object._get_node_status(node_id) == Result.FAILED:
                result_object._status = Result.FAILED
                result_object._end_time = datetime.now(timezone.utc)
                result_object._error = f"Node {result_object._get_node_name(node_id)} failed: \n{result_object._get_node_error(node_id)}"
                result_object.save()
                result_webhook.send_update(result_object)
                return

            elif result_object._get_node_status(node_id) == Result.CANCELLED:
                result_object._status = Result.CANCELLED
                result_object._end_time = datetime.now(timezone.utc)
                result_object.save()
                result_webhook.send_update(result_object)
                return

    # post process the lattice
    result_object._result = _post_process(
        result_object.lattice, result_object.get_all_node_outputs(), order
    )

    result_object._status = Result.COMPLETED
    result_object._end_time = datetime.now(timezone.utc)
    result_object.save(write_source=True)
    result_webhook.send_update(result_object)


def _plan_workflow(result_object: Result) -> None:
    """
    Plan the workflow for execution, assigning the executor to each node
    and assigning some common execution arguments to each node.

    Args:
        result_object: Result object being used for current dispatch

    Returns:
        None
    """

    serialized_tg = result_object.lattice.transport_graph.serialize(metadata_only=True)

    schedule = result_object.lattice.transport_graph.lattice_metadata.get("schedule", False)

    if schedule:
        # Custom scheduling logic
        pass
    else:
        # Default scheduling logic
        workflow_schedule = {"nodes": [], "schedule_quality": 1}
        deserialized_tg = pickle.loads(serialized_tg)

        # Certain metadata fields are transformed and passed to the executor
        for node in deserialized_tg["nodes"]:
            workflow_schedule["nodes"].append(
                {
                    "id": node["id"],
                    "backend": node["metadata"]["backend"][0]
                    if isinstance(node["metadata"]["backend"], list)
                    else node["metadata"]["backend"],
                    # Mutate executor-specific arguments here
                    "backend_args": {"results_dir": result_object.results_dir},
                }
            )

    # Attach the execution plan to the transport graph
    for node in workflow_schedule["nodes"]:
        exec_plan = TaskExecutionMetadata(node["backend"], node["backend_args"])
        result_object._lattice.transport_graph.set_node_value(node["id"], "exec_plan", exec_plan)


def run_workflow(dispatch_id: str, results_dir: str) -> None:
    """
    Plan and run the workflow by loading the result object corresponding to the
    dispatch id and retrieving essential information from it.
    Returns without changing anything if a redispatch is done of a (partially or fully)
    completed workflow with the same dispatch id.

    Args:
        dispatch_id: Dispatch id of the workflow to be run
        results_dir: Directory where the result object is stored

    Returns:
        None
    """

    result_object = rm._get_result_from_file(dispatch_id, results_dir)

    if result_object.status == Result.COMPLETED:
        return

    try:
        _plan_workflow(result_object)
        _run_planned_workflow(result_object)

    except Exception as ex:
        result_object._status = Result.FAILED
        result_object._end_time = datetime.now(timezone.utc)
        result_object._error = "".join(traceback.TracebackException.from_exception(ex).format())
        result_object.save()
        raise


def cancel_workflow(dispatch_id: str) -> None:
    """
    Cancels a dispatched workflow using publish subscribe mechanism
    provided by Dask.

    Args:
        dispatch_id: Dispatch id of the workflow to be cancelled

    Returns:
        None
    """

    shared_var = Variable(dispatch_id, client=dask_client)
    shared_var.set(str(Result.CANCELLED))
