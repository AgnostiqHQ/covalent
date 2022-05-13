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
from concurrent.futures import Future, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from typing import Any, Dict, List

import cloudpickle as pickle

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
from covalent._workflow.lattice import Lattice
from covalent.executor import _executor_manager
from covalent_ui import result_webhook

from .._db.dispatchdb import DispatchDB

app_log = logger.app_log
log_stack_info = logger.log_stack_info


def generate_node_result(
    node_id,
    start_time=None,
    end_time=None,
    status=None,
    output=None,
    error=None,
    stdout=None,
    stderr=None,
    sublattice_result=None,
):

    return {
        "node_id": node_id,
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "output": output,
        "error": error,
        "stdout": stdout,
        "stderr": stderr,
        "sublattice_result": sublattice_result,
    }


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

            edge_data = result_object.lattice.transport_graph.get_edge_data(parent, node_id)

            value = result_object.lattice.transport_graph.get_node_value(parent, "output")
            for e_key, d in edge_data.items():
                key = d["edge_name"]
                values[key] = value

        task_input = {"args": [], "kwargs": {"x": values}}
    else:
        task_input = {"args": [], "kwargs": {}}

        for parent in result_object.lattice.transport_graph.get_dependencies(node_id):

            edge_data = result_object.lattice.transport_graph.get_edge_data(parent, node_id)
            value = result_object.lattice.transport_graph.get_node_value(parent, "output")

            for e_key, d in edge_data.items():
                if d["param_type"] == "arg":
                    task_input["args"].append(value)
                elif d["param_type"] == "kwarg":
                    key = d["edge_name"]
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
    node_id: int,
    dispatch_id: str,
    results_dir: str,
    inputs: Dict,
    serialized_callable: Any,
    selected_executor: Any,
    node_name: str,
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

    inputs = pickle.loads(inputs)
    selected_executor = pickle.loads(selected_executor)

    # the executor is determined during scheduling and provided in the execution metadata
    executor = _executor_manager.get_executor(selected_executor)

    # run the task on the executor and register any failures
    try:

        if node_name.startswith(sublattice_prefix):
            func = serialized_callable.get_deserialized()
            sublattice_result = dispatch_sync(func)(*inputs["args"], **inputs["kwargs"])
            output = sublattice_result.result

            end_time = datetime.now(timezone.utc)

            node_result = generate_node_result(
                node_id=node_id,
                end_time=end_time,
                status=Result.COMPLETED,
                output=output,
                sublattice_result=sublattice_result,
            )

        else:
            output, stdout, stderr = executor.execute(
                function=serialized_callable,
                args=inputs["args"],
                kwargs=inputs["kwargs"],
                dispatch_id=dispatch_id,
                results_dir=results_dir,
                node_id=node_id,
            )

            end_time = datetime.now(timezone.utc)

            node_result = generate_node_result(
                node_id=node_id,
                end_time=end_time,
                status=Result.COMPLETED,
                output=output,
                stdout=stdout,
                stderr=stderr,
            )

    except Exception as ex:
        end_time = datetime.now(timezone.utc)

        node_result = generate_node_result(
            node_id=node_id,
            end_time=end_time,
            status=Result.FAILED,
            error="".join(traceback.TracebackException.from_exception(ex).format()),
        )

    return node_result


def _run_planned_workflow(result_object: Result, thread_pool: ThreadPoolExecutor) -> Result:
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

    def update_node_result(node_result: dict):

        result_object._update_node(**node_result)
        with DispatchDB() as db:
            db.upsert(result_object.dispatch_id, result_object)
        result_object.save()
        result_webhook.send_update(result_object)

    def task_callback(future: Future):
        node_result = future.result()
        update_node_result(node_result)

    result_object._status = Result.RUNNING
    result_object._start_time = datetime.now(timezone.utc)

    order = result_object.lattice.transport_graph.get_topologically_sorted_graph()

    for nodes in order:
        futures: list = []

        for node_id in nodes:
            # Get name of the node for the current task
            node_name = result_object.lattice.transport_graph.get_node_value(node_id, "name")

            if node_name.startswith(
                (subscript_prefix, generator_prefix, parameter_prefix, attr_prefix)
            ):
                if node_name.startswith(parameter_prefix):
                    output = result_object.lattice.transport_graph.get_node_value(node_id, "value")
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
                    node_id=node_id,
                    start_time=datetime.now(timezone.utc),
                    end_time=datetime.now(timezone.utc),
                    status=Result.COMPLETED,
                    output=output,
                )

                continue

            task_input = _get_task_inputs(node_id, node_name, result_object)

            start_time = datetime.now(timezone.utc)
            serialized_callable = result_object.lattice.transport_graph.get_node_value(
                node_id, "function"
            )
            selected_executor = result_object.lattice.transport_graph.get_node_value(
                node_id, "metadata"
            )["executor"]

            update_node_result(
                generate_node_result(
                    node_id=node_id,
                    start_time=start_time,
                    status=Result.RUNNING,
                )
            )

            # Add the task generated for the node to the list of tasks
            future = thread_pool.submit(
                _run_task,
                node_id=node_id,
                dispatch_id=result_object.dispatch_id,
                results_dir=result_object.results_dir,
                serialized_callable=serialized_callable,
                selected_executor=pickle.dumps(selected_executor),
                node_name=node_name,
                inputs=pickle.dumps(task_input),
            )

            future.add_done_callback(task_callback)

            futures.append(future)

        # run the tasks for the current iteration concurrently
        # results are not used right now, but can be in the case of multiprocessing
        wait(futures)
        # del futures

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
                return

            elif result_object._get_node_status(node_id) == Result.CANCELLED:
                result_object._status = Result.CANCELLED
                result_object._end_time = datetime.now(timezone.utc)
                with DispatchDB() as db:
                    db.upsert(result_object.dispatch_id, result_object)
                result_object.save()
                result_webhook.send_update(result_object)
                return

    # post process the lattice
    result_object._result = _post_process(
        result_object.lattice, result_object.get_all_node_outputs(), order
    )

    result_object._status = Result.COMPLETED
    result_object._end_time = datetime.now(timezone.utc)
    with DispatchDB() as db:
        db.upsert(result_object.dispatch_id, result_object)
    result_object.save(write_source=True)
    result_webhook.send_update(result_object)


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


def run_workflow(dispatch_id: str, results_dir: str, tasks_pool: ThreadPoolExecutor) -> None:
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
        _run_planned_workflow(result_object, tasks_pool)

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

    # shared_var = Variable(dispatch_id)
    # shared_var.set(str(Result.CANCELLED))
    pass
