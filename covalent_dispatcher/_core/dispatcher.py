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
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.defaults import parameter_prefix
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent_ui import result_webhook

from . import data_manager as datasvc
from . import runner
from .data_modules.job_manager import set_cancel_requested

app_log = logger.app_log
log_stack_info = logger.log_stack_info


"""
Dispatcher module is responsible for planning and dispatching workflows. The dispatcher

1. Submits tasks to the Runner module.
2. Retrieves information using the Data Manager module.
3. Handles the tasks in terminal (COMPLETED, FAILED, CANCELLED) states.
4. Handles sublattice dispatches once the corresponding graph has been built in the Runner module.
"""


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

        for _, d in edge_data.items():
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
async def _handle_completed_node(result_object, node_id, pending_parents):
    """
    Process the completed node in the transport graph

    Arg(s)
        result_object: Result object associated with the workflow
        node_id: ID of the node in the transport graph
        pending_parents: Parents of this node yet to be executed

    Return(s)
        List of nodes ready to be executed
    """
    g = result_object.lattice.transport_graph._graph

    ready_nodes = []
    app_log.debug(f"Node {node_id} completed")
    for child, edges in g.adj[node_id].items():
        for _ in edges:
            pending_parents[child] -= 1
        if pending_parents[child] < 1:
            app_log.debug(f"Queuing node {child} for execution")
            ready_nodes.append(child)

    return ready_nodes


# Domain: dispatcher
async def _handle_failed_node(result_object, node_id):
    result_object._task_failed = True
    result_object._end_time = datetime.now(timezone.utc)
    app_log.debug(f"Node {result_object.dispatch_id}:{node_id} failed")
    app_log.debug("8A: Failed node upsert statement (run_planned_workflow)")
    datasvc.upsert_lattice_data(result_object.dispatch_id)
    await result_webhook.send_update(result_object)


# Domain: dispatcher
async def _handle_cancelled_node(result_object, node_id):
    result_object._task_cancelled = True
    result_object._end_time = datetime.now(timezone.utc)
    app_log.debug(f"Node {result_object.dispatch_id}:{node_id} cancelled")
    app_log.debug("9: Cancelled node upsert statement (run_planned_workflow)")
    datasvc.upsert_lattice_data(result_object.dispatch_id)
    await result_webhook.send_update(result_object)


# Domain: dispatcher
async def _get_initial_tasks_and_deps(result_object: Result) -> Tuple[int, int, Dict]:
    """Compute the initial batch of tasks to submit and initialize each task's dep count

    Returns: (num_tasks, ready_nodes, pending_parents) where num_tasks is
        the total number of tasks in the graph, ready_nodes is the
        initial list of tasks to dispatch, and pending_parents is a map
        from `node_id` to the number of parents that have yet to
        complete.

    """

    num_tasks = 0
    ready_nodes = []
    pending_parents = {}

    g = result_object.lattice.transport_graph._graph
    for node_id, d in g.in_degree():
        app_log.debug(f"Node {node_id} has {d} parents")

        pending_parents[node_id] = d
        num_tasks += 1
        if d == 0:
            ready_nodes.append(node_id)

    return num_tasks, ready_nodes, pending_parents


# Domain: dispatcher
async def _submit_task(result_object, node_id):
    # Get name of the node for the current task
    node_name = result_object.lattice.transport_graph.get_node_value(node_id, "name")
    node_status = result_object.lattice.transport_graph.get_node_value(node_id, "status")

    # Handle parameter nodes
    if node_name.startswith(parameter_prefix):
        output = result_object.lattice.transport_graph.get_node_value(node_id, "value")
        timestamp = datetime.now(timezone.utc)
        node_result = datasvc.generate_node_result(
            dispatch_id=result_object.dispatch_id,
            node_id=node_id,
            node_name=node_name,
            start_time=timestamp,
            end_time=timestamp,
            status=RESULT_STATUS.COMPLETED,
            output=output,
        )
        await datasvc.update_node_result(result_object, node_result)
        app_log.debug(f"Updated parameter node {node_id}.")

    elif node_status == RESULT_STATUS.COMPLETED:
        timestamp = datetime.now(timezone.utc)
        output = result_object.lattice.transport_graph.get_node_value(node_id, "output")
        node_result = datasvc.generate_node_result(
            dispatch_id=result_object.dispatch_id,
            node_id=node_id,
            node_name=node_name,
            start_time=timestamp,
            end_time=timestamp,
            status=RESULT_STATUS.COMPLETED,
            output=output,
        )
        await datasvc.update_node_result(result_object, node_result)
        app_log.debug(f"Skipped completed node execution {node_name}.")

    else:
        # Gather inputs and dispatch task
        app_log.debug(f"Gathering inputs for task {node_id}.")

        abs_task_input = _get_abstract_task_inputs(node_id, node_name, result_object)
        executor = result_object.lattice.transport_graph.get_node_value(node_id, "metadata")[
            "executor"
        ]
        executor_data = result_object.lattice.transport_graph.get_node_value(node_id, "metadata")[
            "executor_data"
        ]
        coro = runner.run_abstract_task(
            dispatch_id=result_object.dispatch_id,
            node_id=node_id,
            executor=[executor, executor_data],
            node_name=node_name,
            abstract_inputs=abs_task_input,
        )
        app_log.debug(f"Creating task {node_id}.")
        asyncio.create_task(coro)


# Domain: dispatcher
async def _run_planned_workflow(result_object: Result, status_queue: asyncio.Queue) -> Result:
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
    app_log.debug("Starting _run_planned_workflow ...")
    result_object._status = RESULT_STATUS.RUNNING
    result_object._start_time = datetime.now(timezone.utc)
    datasvc.upsert_lattice_data(result_object.dispatch_id)
    app_log.debug(f"Wrote lattice status {result_object._status} to DB.")

    tasks_left, initial_nodes, pending_parents = await _get_initial_tasks_and_deps(result_object)

    unresolved_tasks = 0

    for node_id in initial_nodes:
        unresolved_tasks += 1
        await _submit_task(result_object, node_id)

    while unresolved_tasks > 0:
        app_log.debug(f"{tasks_left} tasks left to complete.")
        app_log.debug(f"Waiting to hear from {unresolved_tasks} tasks.")

        node_id, node_status, detail = await status_queue.get()

        app_log.debug(
            f"Status queue msg for node id {node_id}: {node_status} with detail {detail}."
        )

        if node_status == RESULT_STATUS.RUNNING:
            continue

        # Note: A node status can only be 'DISPATCHING' if it is a sublattice and the corresponding graph has been built.
        if node_status == RESULT_STATUS.DISPATCHING_SUBLATTICE:
            sub_dispatch_id = detail["sub_dispatch_id"]
            run_dispatch(sub_dispatch_id)
            app_log.debug(
                f"Submitted sublattice (dispatch id: {sub_dispatch_id}) to run_dispatch."
            )
            continue

        unresolved_tasks -= 1

        if node_status == RESULT_STATUS.COMPLETED:
            tasks_left -= 1
            ready_nodes = await _handle_completed_node(result_object, node_id, pending_parents)
            for node_id in ready_nodes:
                unresolved_tasks += 1
                await _submit_task(result_object, node_id)

        if node_status == RESULT_STATUS.FAILED:
            await _handle_failed_node(result_object, node_id)
            continue

        if node_status == RESULT_STATUS.CANCELLED:
            await _handle_cancelled_node(result_object, node_id)
            continue

    if result_object._task_failed or result_object._task_cancelled:
        app_log.debug(f"Workflow {result_object.dispatch_id} cancelled or failed")
        failed_nodes = result_object._get_failed_nodes()
        failed_nodes = map(lambda x: f"{x[0]}: {x[1]}", failed_nodes)
        failed_nodes_msg = "\n".join(failed_nodes)
        result_object._error = "The following tasks failed:\n" + failed_nodes_msg
        result_object._status = (
            RESULT_STATUS.FAILED if result_object._task_failed else RESULT_STATUS.CANCELLED
        )
        return result_object

    app_log.debug(
        f"Tasks for {result_object.dispatch_id} finished running. Updating result webhook ..."
    )
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
    app_log.debug(f"Starting run_workflow for dispatch id {result_object.dispatch_id} ...")
    if result_object.status == RESULT_STATUS.COMPLETED:
        datasvc.finalize_dispatch(result_object.dispatch_id)
        return result_object

    try:
        _plan_workflow(result_object)
        status_queue = datasvc.get_status_queue(result_object.dispatch_id)
        result_object = await _run_planned_workflow(result_object, status_queue)

    except Exception as ex:
        app_log.error(f"Exception during _run_planned_workflow: {ex}")

        error_msg = "".join(traceback.TracebackException.from_exception(ex).format())
        result_object._status = RESULT_STATUS.FAILED
        result_object._error = error_msg
        result_object._end_time = datetime.now(timezone.utc)

    finally:
        await datasvc.persist_result(result_object.dispatch_id)
        datasvc.finalize_dispatch(result_object.dispatch_id)

    return result_object


# Domain: dispatcher
async def cancel_dispatch(dispatch_id: str, task_ids: List[int] = None) -> None:
    """
    Cancel an entire dispatch or a specific set of tasks within it

    Arg(s)
        dispatch_id: Dispatch ID of the lattice
        task_ids: List of tasks from the lattice that are to be cancelled. Defaults to [] (entire lattice)

    Return(s)
        None
    """
    if task_ids is None:
        task_ids = []
    if not dispatch_id:
        return

    res_object = datasvc.get_result_object(dispatch_id)
    if res_object is None:
        return

    tg = res_object.lattice.transport_graph
    if task_ids:
        app_log.debug(f"Cancelling tasks {task_ids} in dispatch {dispatch_id}")
    else:
        task_ids = list(tg._graph.nodes)
        app_log.debug(f"Cancelling dispatch {dispatch_id}")

    await set_cancel_requested(dispatch_id, task_ids)
    await runner.cancel_tasks(dispatch_id, task_ids)

    # Recursively cancel running sublattice dispatches
    sub_ids = list(map(lambda x: tg.get_node_value(x, "sub_dispatch_id"), task_ids))
    for sub_dispatch_id in sub_ids:
        await cancel_dispatch(sub_dispatch_id)


def run_dispatch(dispatch_id: str) -> asyncio.Future:
    """
    Run the workflow and return immediately

    Arg(s)
        dispatch_id: Dispatch ID of the lattice

    Return(s)
        asyncio.Future

    """
    app_log.debug(f"Running dispatch with dispatch_id: {dispatch_id}.")
    result_object = datasvc.get_result_object(dispatch_id)
    return asyncio.create_task(run_workflow(result_object))
