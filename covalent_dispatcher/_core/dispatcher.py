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
import os
import traceback
from datetime import datetime, timezone
from typing import Dict, Tuple

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.defaults import parameter_prefix
from covalent._shared_files.util_classes import RESULT_STATUS

from . import data_manager as datasvc
from . import runner, runner_exp
from .data_manager import SRVResult

app_log = logger.app_log
log_stack_info = logger.log_stack_info
_global_event_queue = asyncio.Queue()
_status_queues = {}

NEW_RUNNER_ENABLED = get_config("dispatcher.force_legacy_runner") == "false"
POSTPROCESS_SEPARATELY = os.environ.get("COVALENT_POSTPROCESS_SEPARATELY") == "1"


# Domain: dispatcher
async def _get_abstract_task_inputs(dispatch_id: str, node_id: int, node_name: str) -> dict:
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

    for edge in await datasvc.get_incoming_edges(dispatch_id, node_id):

        parent = edge["source"]

        d = edge["attrs"]
        # value = result_object.lattice.transport_graph.get_node_value(parent, "output")

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
async def _handle_completed_node(result_object: SRVResult, node_id: int, pending_parents: Dict):
    g = result_object.lattice.transport_graph

    ready_nodes = []
    app_log.debug(f"Node {node_id} completed")
    for child in g.get_successors(node_id):
        pending_parents[child] -= 1
        if pending_parents[child] < 1:
            app_log.debug(f"Queuing node {child} for execution")
            ready_nodes.append(child)

    return ready_nodes


# Domain: dispatcher
async def _handle_failed_node(result_object: SRVResult, node_id: int):
    app_log.debug(f"Node {result_object.dispatch_id}:{node_id} failed")
    app_log.debug("8A: Failed node upsert statement (run_planned_workflow)")
    # result_object.commit()
    # datasvc.upsert_lattice_data(result_object.dispatch_id)


# Domain: dispatcher
async def _handle_cancelled_node(result_object: SRVResult, node_id: int):
    app_log.debug(f"Node {result_object.dispatch_id}:{node_id} cancelled")
    app_log.debug("9: Cancelled node upsert statement (run_planned_workflow)")
    # datasvc.upsert_lattice_data(result_object.dispatch_id)
    # result_object.commit()


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

    dispatch_id = result_object.dispatch_id

    # Get name of the node for the current task
    node_name = await datasvc.get_electron_attribute(dispatch_id, node_id, "name")
    app_log.debug(f"7A: Node name: {node_name} (run_planned_workflow).")

    # Handle parameter nodes
    if node_name.startswith(parameter_prefix):
        app_log.debug("7C: Parameter if block (run_planned_workflow).")
        output = await datasvc.get_electron_attribute(dispatch_id, node_id, "value")
        app_log.debug(f"7C: Node output: {output} (run_planned_workflow).")
        app_log.debug("8: Starting update node (run_planned_workflow).")

        node_result = {
            "node_id": node_id,
            "start_time": datetime.now(timezone.utc),
            "end_time": datetime.now(timezone.utc),
            "status": Result.COMPLETED,
            "output": output,
        }
        await datasvc.update_node_result(dispatch_id, node_result)
        app_log.debug("8A: Update node success (run_planned_workflow).")

    else:
        # Gather inputs and dispatch task
        app_log.debug(f"Gathering inputs for task {node_id} (run_planned_workflow).")

        abs_task_input = await _get_abstract_task_inputs(dispatch_id, node_id, node_name)

        selected_executor = await datasvc.get_electron_attribute(dispatch_id, node_id, "executor")
        selected_executor_data = await datasvc.get_electron_attribute(
            dispatch_id, node_id, "executor_data"
        )

        app_log.debug(f"Submitting task {node_id} to executor")

        if NEW_RUNNER_ENABLED:
            app_log.debug(f"Using new runner for task {node_id}")
            coro = runner_exp.run_abstract_task(
                dispatch_id=result_object.dispatch_id,
                node_id=node_id,
                selected_executor=[selected_executor, selected_executor_data],
                node_name=node_name,
                abstract_inputs=abs_task_input,
            )
        else:
            app_log.debug(f"Using legacy runner for task {node_id}")
            coro = runner.run_abstract_task(
                dispatch_id=result_object.dispatch_id,
                node_id=node_id,
                selected_executor=[selected_executor, selected_executor_data],
                node_name=node_name,
                abstract_inputs=abs_task_input,
            )
        asyncio.create_task(coro)


# Domain: dispatcher
async def _run_planned_workflow(
    result_object: SRVResult, status_queue: asyncio.Queue
) -> SRVResult:
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
    result_object._status = Result.RUNNING
    result_object._start_time = datetime.now(timezone.utc)

    app_log.debug(
        f"4: Workflow status changed to running {result_object.dispatch_id} (run_planned_workflow)."
    )
    result_object.commit()
    app_log.debug("5: Wrote lattice status to DB (run_planned_workflow).")

    tasks_left, initial_nodes, pending_parents = await _get_initial_tasks_and_deps(result_object)

    unresolved_tasks = 0
    resolved_tasks = 0

    for node_id in initial_nodes:
        unresolved_tasks += 1
        await _submit_task(result_object, node_id)

    while unresolved_tasks > 0:
        app_log.debug(f"{tasks_left} tasks left to complete")
        app_log.debug(f"Waiting to hear from {unresolved_tasks} tasks")
        node_id, node_status, detail = await status_queue.get()

        app_log.debug(f"Received node status update {node_id}: {node_status}")

        if node_status == Result.RUNNING:
            continue

        if node_status == RESULT_STATUS.DISPATCHING:
            sub_dispatch_id = detail["sub_dispatch_id"]
            run_dispatch(sub_dispatch_id)
            app_log.debug(f"Running sublattice dispatch {sub_dispatch_id}")
            continue

        unresolved_tasks -= 1

        if node_status == Result.COMPLETED:
            tasks_left -= 1
            ready_nodes = await _handle_completed_node(result_object, node_id, pending_parents)
            for node_id in ready_nodes:
                unresolved_tasks += 1
                await _submit_task(result_object, node_id)

        if node_status == Result.FAILED:
            await _handle_failed_node(result_object, node_id)
            continue

        if node_status == Result.CANCELLED:
            await _handle_cancelled_node(result_object, node_id)
            continue

    await _finalize_dispatch(result_object.dispatch_id)

    return result_object


def _plan_workflow(result_object: SRVResult) -> None:
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


async def run_workflow(result_object: SRVResult) -> SRVResult:
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
        datasvc.finalize_dispatch(result_object.dispatch_id)
        return result_object

    try:
        _plan_workflow(result_object)
        dispatch_id = result_object.dispatch_id
        _status_queues[dispatch_id] = asyncio.Queue()
        result_object = await _run_planned_workflow(result_object, _status_queues[dispatch_id])

    except Exception as ex:
        app_log.error(f"Exception during _run_planned_workflow: {ex}")

        error_msg = "".join(traceback.TracebackException.from_exception(ex).format())
        result_object._status = Result.FAILED
        result_object._error = error_msg
        result_object._end_time = datetime.now(timezone.utc)

    finally:
        result_object.commit()
        await datasvc.persist_result(result_object.dispatch_id)
        datasvc.finalize_dispatch(result_object.dispatch_id)
        _status_queues.pop(result_object.dispatch_id)
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


def run_dispatch(dispatch_id: str) -> asyncio.Future:
    result_object = datasvc.get_result_object(dispatch_id)
    return asyncio.create_task(run_workflow(result_object))


async def notify_node_status(
    dispatch_id: str, node_id: int, status: RESULT_STATUS, detail: Dict = {}
):
    msg = {
        "dispatch_id": dispatch_id,
        "node_id": node_id,
        "status": status,
        "detail": detail,
    }
    status_queue = _status_queues[dispatch_id]
    await status_queue.put((node_id, status, detail))


async def _finalize_dispatch(dispatch_id: str):

    incomplete_tasks = await datasvc.get_incomplete_tasks(dispatch_id)
    failed = incomplete_tasks["failed"]
    cancelled = incomplete_tasks["cancelled"]
    if failed or cancelled:
        app_log.debug(f"Workflow {dispatch_id} cancelled or failed")
        failed_nodes = failed
        failed_nodes = map(lambda x: f"{x[0]}: {x[1]}", failed_nodes)
        failed_nodes_msg = "\n".join(failed_nodes)
        error_msg = "The following tasks failed:\n" + failed_nodes_msg
        ts = datetime.now(timezone.utc)
        status = Result.FAILED if failed else Result.CANCELLED
        result_update = datasvc.generate_dispatch_result(
            dispatch_id,
            status=status,
            error=error_msg,
            end_time=ts,
        )
        await datasvc.update_dispatch_result(dispatch_id, result_update)

    app_log.debug("8: All tasks finished running (run_planned_workflow)")

    result_object = datasvc.get_result_object(dispatch_id)
    if POSTPROCESS_SEPARATELY:
        result_object = await runner.postprocess_workflow(dispatch_id)
    else:
        app_log.debug("Workflow already postprocessed")
