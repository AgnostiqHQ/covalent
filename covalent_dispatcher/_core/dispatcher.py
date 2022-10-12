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

import asyncio
import json
import traceback
from asyncio import Queue
from datetime import datetime, timezone
from functools import partial
from typing import Any, Dict

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.context_managers import active_lattice_manager
from covalent._shared_files.defaults import parameter_prefix, prefix_separator, sublattice_prefix
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import TransportableObject
from covalent_ui import result_webhook

from .._db import update, upsert
from .._db.write_result_to_db import update_lattices_data, write_lattice_error
from . import result as resultsvc
from . import runner

app_log = logger.app_log
log_stack_info = logger.log_stack_info


# This is to be run out-of-process
def _build_sublattice_graph(sub: Lattice, *args, **kwargs):
    sub.build_graph(*args, **kwargs)
    return sub.serialize_to_json()


async def _dispatch_sync_sublattice(
    parent_result_object: Result,
    parent_electron_id: int,
    inputs: Dict,
    serialized_callable: Any,
    workflow_executor: Any,
) -> str:
    """Dispatch a sublattice using the workflow_executor."""

    app_log.debug("Inside _dispatch_sync_sublattice")

    try:
        short_name, object_dict = workflow_executor

        if short_name == "client":
            app_log.error("No executor selected for dispatching sublattices")
            raise RuntimeError("No executor selected for dispatching sublattices")

    except Exception as ex:
        app_log.debug(f"Exception when trying to determine sublattice executor: {ex}")
        return None

    sub_dispatch_inputs = {"args": [serialized_callable], "kwargs": inputs["kwargs"]}
    for arg in inputs["args"]:
        sub_dispatch_inputs["args"].append(arg)

    # Build the sublattice graph. This must be run
    # externally since it involves deserializing the
    # sublattice workflow function.
    fut = asyncio.create_task(
        runner._run_task(
            result_object=parent_result_object,
            node_id=-1,
            serialized_callable=TransportableObject.make_transportable(_build_sublattice_graph),
            selected_executor=workflow_executor,
            node_name="build_sublattice_graph",
            call_before=[],
            call_after=[],
            inputs=sub_dispatch_inputs,
            workflow_executor=workflow_executor,
        )
    )

    res = await fut
    if res["status"] == Result.COMPLETED:
        json_sublattice = json.loads(res["output"].json)

        sub_result_object = resultsvc.initialize_result_object(
            json_sublattice, parent_result_object, parent_electron_id
        )
        app_log.debug(f"Sublattice dispatch id: {sub_result_object.dispatch_id}")

        return await run_workflow(sub_result_object)
    else:
        return None


# Domain: dispatcher
def _get_abstract_task_inputs(node_id: int, node_name: str, result_object: Result) -> dict:
    """Return placeholders for the required inputs for a task execution.

    Args:
        node_id: Node id of this task in the transport graph.
        node_name: Name of the node.
        result_object: Result object to be used to update and store execution related
                       info including the results.

    Returns: inputs: Input dictionary to be passed to the task with
        `node_id` placeholders for args, kwargs. These are to be
        resolved to their values later.
    """

    abstract_task_input = {"args": [], "kwargs": {}}

    for parent in result_object.lattice.transport_graph.get_dependencies(node_id):

        edge_data = result_object.lattice.transport_graph.get_edge_data(parent, node_id)
        # value = result_object.lattice.transport_graph.get_node_value(parent, "output")

        for e_key, d in edge_data.items():
            if not d.get("wait_for"):
                if d["param_type"] == "arg":
                    abstract_task_input["args"].append((parent, d["arg_index"]))
                elif d["param_type"] == "kwarg":
                    key = d["edge_name"]
                    abstract_task_input["kwargs"][key] = parent

    sorted_args = sorted(abstract_task_input["args"], key=lambda x: x[1])
    abstract_task_input["args"] = [x[0] for x in sorted_args]

    return abstract_task_input


# Domain: dispatcher
# This is to be run out-of-process
def _post_process(lattice: Lattice, node_outputs: Dict) -> Any:
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

    ordered_node_outputs = []
    app_log.debug(f"node_outputs: {node_outputs}")
    app_log.debug(f"node_outputs: {node_outputs.items()}")
    for i, item in enumerate(node_outputs.items()):
        key, val = item
        app_log.debug(f"Here's the key: {key}")
        if not key.startswith(prefix_separator) or key.startswith(sublattice_prefix):
            ordered_node_outputs.append((i, val))

    with active_lattice_manager.claim(lattice):
        lattice.post_processing = True
        lattice.electron_outputs = ordered_node_outputs
        args = [arg.get_deserialized() for arg in lattice.args]
        kwargs = {k: v.get_deserialized() for k, v in lattice.kwargs.items()}
        workflow_function = lattice.workflow_function.get_deserialized()
        result = workflow_function(*args, **kwargs)
        lattice.post_processing = False
        return result


# Domain: dispatcher
async def _handle_completed_node(result_object, node_id, pending_deps):
    g = result_object.lattice.transport_graph._graph

    ready_nodes = []
    app_log.debug(f"Node {node_id} completed")
    for child, edges in g.adj[node_id].items():
        for edge in edges:
            pending_deps[child] -= 1
        if pending_deps[child] < 1:
            app_log.debug(f"Queuing node {child} for execution")
            ready_nodes.append(child)

    return ready_nodes


# Domain: dispatcher
async def _handle_failed_node(result_object, node_id):
    result_object._status = Result.FAILED
    result_object._end_time = datetime.now(timezone.utc)
    result_object._error = f"Node {result_object._get_node_name(node_id)} failed: \n{result_object._get_node_error(node_id)}"
    app_log.warning("8A: Failed node upsert statement (run_planned_workflow)")
    upsert._lattice_data(result_object)
    await result_webhook.send_update(result_object)


# Domain: dispatcher
async def _handle_cancelled_node(result_object, node_id):
    result_object._status = Result.CANCELLED
    result_object._end_time = datetime.now(timezone.utc)
    app_log.warning("9: Failed node upsert statement (run_planned_workflow)")
    upsert._lattice_data(result_object)
    await result_webhook.send_update(result_object)


# Domain: dispatcher
async def _initialize_deps_and_queue(result_object: Result) -> int:
    """Initialize the data structures controlling when tasks are queued for execution.

    Returns the total number of nodes in the transport graph."""

    num_tasks = 0
    ready_nodes = []
    pending_deps = {}

    g = result_object.lattice.transport_graph._graph
    for node_id, d in g.in_degree():
        app_log.debug(f"Node {node_id} has {d} parents")

        pending_deps[node_id] = d
        num_tasks += 1
        if d == 0:
            ready_nodes.append(node_id)

    return num_tasks, ready_nodes, pending_deps


# Domain: dispatcher
async def _postprocess_workflow(result_object: Result) -> Result:
    """
    Postprocesses a workflow with a completed computational graph

    Args:
        result_object: Result object being used for current dispatch

    Returns:
        The postprocessed result object
    """

    # Executor for post_processing
    pp_executor = result_object.lattice.get_metadata("workflow_executor")
    pp_executor_data = result_object.lattice.get_metadata("workflow_executor_data")
    post_processor = [pp_executor, pp_executor_data]

    result_object._status = Result.POSTPROCESSING
    upsert._lattice_data(result_object)

    app_log.debug(f"Preparing to post-process workflow {result_object.dispatch_id}")

    if pp_executor == "client":
        app_log.debug("Workflow to be postprocessed client side")
        result_object._status = Result.PENDING_POSTPROCESSING
        result_object._end_time = datetime.now(timezone.utc)
        upsert._lattice_data(result_object)
        await result_webhook.send_update(result_object)
        return result_object

    post_processing_inputs = {}
    post_processing_inputs["args"] = [
        TransportableObject.make_transportable(result_object.lattice),
        TransportableObject.make_transportable(result_object.get_all_node_outputs()),
    ]
    post_processing_inputs["kwargs"] = {}

    try:
        future = asyncio.create_task(
            runner._run_task(
                result_object=result_object,
                node_id=-1,
                serialized_callable=TransportableObject(_post_process),
                selected_executor=post_processor,
                node_name="post_process",
                call_before=[],
                call_after=[],
                inputs=post_processing_inputs,
                workflow_executor=post_processor,
            )
        )
        pp_start_time = datetime.now(timezone.utc)
        app_log.debug(
            f"Submitted post-processing job to executor {post_processor} at {pp_start_time}"
        )

        post_process_result = await future
    except Exception as ex:
        app_log.debug(f"Exception during post-processing: {ex}")
        result_object._status = Result.POSTPROCESSING_FAILED
        result_object._error = "Post-processing failed"
        result_object._end_time = datetime.now(timezone.utc)
        upsert._lattice_data(result_object)
        await result_webhook.send_update(result_object)

        return result_object

    if post_process_result["status"] != Result.COMPLETED:
        err = post_process_result["stderr"]
        app_log.debug(f"Post-processing failed: {err}")
        result_object._status = Result.POSTPROCESSING_FAILED
        result_object._error = f"Post-processing failed: {err}"
        result_object._end_time = datetime.now(timezone.utc)
        upsert._lattice_data(result_object)
        await result_webhook.send_update(result_object)

        return result_object

    pp_end_time = post_process_result["end_time"]
    app_log.debug(f"Post-processing completed at {pp_end_time}")
    result_object._result = post_process_result["output"]
    result_object._status = Result.COMPLETED
    result_object._end_time = datetime.now(timezone.utc)

    app_log.debug(
        f"10: Successfully post-processed result {result_object.dispatch_id} (run_planned_workflow)"
    )

    return result_object


# Domain: dispatcher
async def _submit_task(result_object, node_id, pending_deps, status_queue, task_futures):

    # Get name of the node for the current task
    node_name = result_object.lattice.transport_graph.get_node_value(node_id, "name")
    app_log.debug(f"7A: Node name: {node_name} (run_planned_workflow).")

    # Handle parameter nodes
    if node_name.startswith(parameter_prefix):
        app_log.debug("7C: Parameter if block (run_planned_workflow).")
        output = result_object.lattice.transport_graph.get_node_value(node_id, "value")
        app_log.debug(f"7C: Node output: {output} (run_planned_workflow).")
        app_log.debug("8: Starting update node (run_planned_workflow).")

        node_result = {
            "node_id": node_id,
            "start_time": datetime.now(timezone.utc),
            "end_time": datetime.now(timezone.utc),
            "status": Result.COMPLETED,
            "output": output,
        }
        await resultsvc._update_node_result(result_object, node_result, pending_deps, status_queue)
        app_log.debug("8A: Update node success (run_planned_workflow).")

    else:

        # Executor for post_processing and dispatching sublattices
        pp_executor = result_object.lattice.get_metadata("workflow_executor")
        pp_executor_data = result_object.lattice.get_metadata("workflow_executor_data")
        post_processor = [pp_executor, pp_executor_data]

        # Gather inputs and dispatch task
        app_log.debug(f"Gathering inputs for task {node_id} (run_planned_workflow).")

        abs_task_input = _get_abstract_task_inputs(node_id, node_name, result_object)

        start_time = datetime.now(timezone.utc)

        selected_executor = result_object.lattice.transport_graph.get_node_value(
            node_id, "metadata"
        )["executor"]

        selected_executor_data = result_object.lattice.transport_graph.get_node_value(
            node_id, "metadata"
        )["executor_data"]

        app_log.debug(f"Collecting deps for task {node_id}")

        node_result = resultsvc.generate_node_result(
            node_id=node_id,
            start_time=start_time,
            status=Result.RUNNING,
        )
        await resultsvc._update_node_result(result_object, node_result, pending_deps, status_queue)
        app_log.debug(f"7: Marking node {node_id} as running (_submit_task)")

        app_log.debug(f"Submitting task {node_id} to executor")

        run_task_callable = partial(
            runner._run_abstract_task,
            result_object=result_object,
            node_id=node_id,
            selected_executor=[selected_executor, selected_executor_data],
            node_name=node_name,
            abstract_inputs=abs_task_input,
            workflow_executor=post_processor,
        )

        # Add the task generated for the node to the list of tasks
        future = asyncio.create_task(
            runner._run_task_and_update(
                run_task_callable=run_task_callable,
                result_object=result_object,
                pending_deps=pending_deps,
                status_queue=status_queue,
            )
        )

        task_futures.append(future)


# Domain: dispatcher
async def _run_planned_workflow(result_object: Result, status_queue: Queue = None) -> Result:
    """
    Run the workflow in the topological order of their position on the
    transport graph. Does this in an asynchronous manner so that nodes
    at the same level are executed in parallel. Also updates the status
    of the whole workflow execution.

    Args:
        result_object: Result object being used for current dispatch
        status_queue: message queue for notifying the main loop of status updates

    Returns:
        None
    """

    app_log.debug("3: Inside run_planned_workflow (run_planned_workflow).")

    if not status_queue:
        status_queue = Queue()

    task_futures: list = []

    app_log.debug(
        f"4: Workflow status changed to running {result_object.dispatch_id} (run_planned_workflow)."
    )

    result_object._status = Result.RUNNING
    result_object._start_time = datetime.now(timezone.utc)

    upsert._lattice_data(result_object)
    app_log.debug("5: Wrote lattice status to DB (run_planned_workflow).")

    tasks_left, initial_nodes, pending_deps = await _initialize_deps_and_queue(result_object)

    unresolved_tasks = 0
    resolved_tasks = 0

    for node_id in initial_nodes:
        unresolved_tasks += 1
        await _submit_task(result_object, node_id, pending_deps, status_queue, task_futures)

    while unresolved_tasks > 0:
        app_log.debug(f"{tasks_left} tasks left to complete")
        app_log.debug(f"Waiting to hear from {unresolved_tasks} tasks")
        node_id, node_status = await status_queue.get()

        app_log.debug(f"Processing result for node {node_id}")

        if node_status == Result.RUNNING:
            continue

        unresolved_tasks -= 1

        if node_status == Result.COMPLETED:
            tasks_left -= 1
            ready_nodes = await _handle_completed_node(result_object, node_id, pending_deps)
            for node_id in ready_nodes:
                unresolved_tasks += 1
                await _submit_task(
                    result_object, node_id, pending_deps, status_queue, task_futures
                )

        if node_status == Result.FAILED:
            await _handle_failed_node(result_object, node_id)

        if node_status == Result.CANCELLED:
            await _handle_cancelled_node(result_object, node_id)

    if result_object._status in [Result.FAILED, Result.CANCELLED]:
        app_log.debug(f"Workflow {result_object.dispatch_id} cancelled or failed")
        return result_object

    app_log.debug("8: All tasks finished running (run_planned_workflow)")

    result_object = await _postprocess_workflow(result_object)

    update.persist(result_object)
    await result_webhook.send_update(result_object)

    return result_object


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


async def run_workflow(result_object: Result) -> Result:
    """
    Plan and run the workflow by loading the result object corresponding to the
    dispatch id and retrieving essential information from it.
    Returns without changing anything if a redispatch is done of a (partially or fully)
    completed workflow with the same dispatch id.

    Args:
        dispatch_id: Dispatch id of the workflow to be run
        results_dir: Directory where the result object is stored

    Returns:
        The result object from the workflow execution
    """

    app_log.debug("Inside run_workflow.")

    if result_object.status == Result.COMPLETED:
        return result_object

    try:
        _plan_workflow(result_object)
        result_object = await _run_planned_workflow(result_object)

    except Exception as ex:
        app_log.error(f"Exception during _run_planned_workflow: {ex}")
        update_lattices_data(
            result_object.dispatch_id,
            status=str(Result.FAILED),
            completed_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        write_lattice_error(
            result_object.dispatch_id,
            "".join(traceback.TracebackException.from_exception(ex).format()),
        )
        raise

    return result_object


# Domain: dispatcher
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
