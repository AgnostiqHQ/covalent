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

import socket
import traceback
from datetime import datetime, timezone
from typing import Any, Coroutine, Dict, List

import dask
from dask.distributed import Client, Variable

from covalent import dispatch_sync
from covalent._results_manager import Result
from covalent._results_manager import results_manager as rm
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
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
from covalent.executor import _executor_manager
from covalent.notify.notify import NotifyEndpoint
from covalent_ui import result_webhook

from .._db.dispatchdb import DispatchDB

app_log = logger.app_log
log_stack_info = logger.log_stack_info

dask_client = Client(processes=False, dashboard_address=":0")


def _get_task_inputs(node_id: int, node_name: str, result_object: Result) -> dict:
    """
    Return the required inputs for a task execution.
    This makes sure that any node with child nodes isn't executed twice and fetches the
    result of parent node to use as input for the child node.

    Args:
        node_id: Node id of this task in the transport graph.
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
            for parent in result_object.lattice.transport_graph.get_dependencies(node_id)
        ]
        task_input = {"args": [], "kwargs": {"x": values}}
    elif node_name.startswith(electron_dict_prefix):
        values = {}
        for parent in result_object.lattice.transport_graph.get_dependencies(node_id):
            key = result_object.lattice.transport_graph.get_edge_value(
                parent, node_id, "edge_name"
            )
            value = result_object.lattice.transport_graph.get_node_value(parent, "output")
            values[key] = value
        task_input = {"args": [], "kwargs": {"x": values}}
    else:
        task_input = {"args": [], "kwargs": {}}

        for parent in result_object.lattice.transport_graph.get_dependencies(node_id):

            param_type = result_object.lattice.transport_graph.get_edge_value(
                parent, node_id, "param_type"
            )

            value = result_object.lattice.transport_graph.get_node_value(parent, "output")

            if param_type == "arg":
                task_input["args"].append(value)

            elif param_type == "kwarg":
                key = result_object.lattice.transport_graph.get_edge_value(
                    parent, node_id, "edge_name"
                )

                task_input["kwargs"][key] = value
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

    ordered_node_outputs = [
        val
        for key, val in node_outputs.items()
        if not key.startswith(prefix_separator) or key.startswith(sublattice_prefix)
    ]

    with active_lattice_manager.claim(lattice):
        lattice.post_processing = True
        lattice.electron_outputs = ordered_node_outputs
        result = lattice.workflow_function(*lattice.args, **lattice.kwargs)
        lattice.post_processing = False
        return result


def _run_task(
    inputs: Dict,
    result_object: Result,
    node_id: int,
) -> None:
    """
    Run a task with given inputs on the selected executor.
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
    app_log.debug("_run_task")
    serialized_callable = result_object.lattice.transport_graph.get_node_value(node_id, "function")
    selected_executor = result_object.lattice.transport_graph.get_node_value(node_id, "metadata")[
        "executor"
    ]
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
        with DispatchDB() as db:
            db.upsert(result_object.dispatch_id, result_object)
        result_object.save()
        result_webhook.send_update(result_object)

        return

    if result_object._get_node_status(node_id) == Result.COMPLETED:
        return

    # the executor is determined during scheduling and provided in the execution metadata
    executor = _executor_manager.get_executor(selected_executor)

    # run the task on the executor and register any failures
    app_log.debug("run the task on the executor")
    try:
        start_time = datetime.now(timezone.utc)
        result_object._update_node(
            node_id, node_name, start_time, None, Result.RUNNING, None, None
        )
        with DispatchDB() as db:
            db.upsert(result_object.dispatch_id, result_object)
        result_object.save()
        result_webhook.send_update(result_object)

        if node_name.startswith(sublattice_prefix):
            func = serialized_callable.get_deserialized()
            sublattice_result = dispatch_sync(func)(*inputs["args"], **inputs["kwargs"])
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
                inputs["args"],
                inputs["kwargs"],
                result_object.dispatch_id,
                result_object.results_dir,
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
    with DispatchDB() as db:
        db.upsert(result_object.dispatch_id, result_object)
    result_object.save()
    app_log.debug("_run_task end")
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
    app_log.debug("_run_planned_workflow")
    shared_var = Variable(result_object.dispatch_id, client=dask_client)
    shared_var.set(str(Result.RUNNING))

    result_object._status = Result.RUNNING
    result_object._start_time = datetime.now(timezone.utc)

    order = result_object.lattice.transport_graph.get_topologically_sorted_graph()

    for nodes in order:
        tasks: List[Coroutine] = []

        for node_id in nodes:
            # Get name of the node for the current task
            node_name = result_object.lattice.transport_graph.get_node_value(node_id, "name")

            if node_name.startswith(
                (subscript_prefix, generator_prefix, parameter_prefix, attr_prefix)
            ):
                if node_name.startswith(parameter_prefix):
                    output = result_object.lattice.transport_graph.get_node_value(node_id, "value")
                    print(node_id, node_name, output)
                else:
                    parent = result_object.lattice.transport_graph.get_dependencies(node_id)[0]
                    output = result_object.lattice.transport_graph.get_node_value(parent, "output")

                    if node_name.startswith(attr_prefix):
                        attr = result_object.lattice.transport_graph.get_node_value(
                            node_id, "attribute_name"
                        )
                        output = getattr(output, attr)
                    else:
                        key = result_object.lattice.transport_graph.get_node_value(node_id, "key")
                        output = output[key]

                result_object._update_node(
                    node_id,
                    f"{node_name}({node_id})",
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc),
                    Result.COMPLETED,
                    output,
                    None,
                )

                continue

            task_input = _get_task_inputs(node_id, node_name, result_object)
            app_log.debug("Adding the task to the list for dask.")
            app_log.debug("task_input")
            app_log.debug(task_input)
            app_log.debug("result_object")
            app_log.debug(result_object)
            app_log.debug("node_id")
            app_log.debug(node_id)
            # Add the task generated for the node to the list of tasks
            tasks.append(dask.delayed(_run_task)(task_input, result_object, node_id))
        app_log.debug("Running tasks in parallel using dask.")
        # run the tasks for the current iteration in parallel
        dask.compute(*tasks)

        # When one or more nodes failed in the last iteration, don't iterate further
        for node_id in nodes:
            if result_object._get_node_status(node_id) == Result.FAILED:
                result_object._status = Result.FAILED
                result_object._end_time = datetime.now(timezone.utc)
                result_object._error = f"Node {result_object._get_node_name(node_id)} failed: \n{result_object._get_node_error(node_id)}"
                with DispatchDB() as db:
                    db.upsert(result_object.dispatch_id, result_object)
                result_object.save()
                result_webhook.send_update(result_object)
                _notify_endpoints(
                    result_object.dispatch_id,
                    result_object._status,
                    result_object.lattice.get_metadata("notify"),
                )
                return

            elif result_object._get_node_status(node_id) == Result.CANCELLED:
                result_object._status = Result.CANCELLED
                result_object._end_time = datetime.now(timezone.utc)
                with DispatchDB() as db:
                    db.upsert(result_object.dispatch_id, result_object)
                result_object.save()
                app_log.debug("result cancelled")
                result_webhook.send_update(result_object)
                _notify_endpoints(
                    result_object.dispatch_id,
                    result_object._status,
                    result_object.lattice.get_metadata("notify"),
                )
                return

    # post process the lattice
    app_log.debug("post process the lattice")
    result_object._result = _post_process(
        result_object.lattice, result_object.get_all_node_outputs(), order
    )

    result_object._status = Result.COMPLETED
    result_object._end_time = datetime.now(timezone.utc)
    with DispatchDB() as db:
        db.upsert(result_object.dispatch_id, result_object)
    result_object.save(write_source=True)
    result_webhook.send_update(result_object)
    _notify_endpoints(
        result_object.dispatch_id,
        result_object._status,
        result_object.lattice.get_metadata("notify"),
    )


def _notify_endpoints(dispatch_id: str, status: str, endpoints: List[NotifyEndpoint]) -> None:
    ui_port = get_config("user_interface.port")
    ui_url = f"http://{socket.getfqdn()}:{ui_port}/{dispatch_id}"
    notification_message = (
        f"Covalent lattice has finished running with status '{status}'. View results at {ui_url}."
    )

    for endpoint in endpoints:
        endpoint.notify(notification_message)


def _plan_workflow(result_object: Result) -> None:
    """
    Function to plan a workflow according to a schedule.
    Planning means to decide which executors (along with their arguments) will
    be used by each node.

    Args:
        result_object: Result object being used for current dispatch

    Returns:
        None
    """

    if result_object.lattice.get_metadata("schedule"):
        # Custom scheduling logic of the format:
        # scheduled_executors = get_schedule(result_object)

        # for node_id, executor in scheduled_executors.items():
        #    result_object.lattice.transport_graph.set_node_value(node_id, "executor", executor)
        pass


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
