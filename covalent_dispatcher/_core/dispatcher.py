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

import networkx as nx

from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.defaults import WAIT_EDGE_NAME, parameter_prefix
from covalent._shared_files.util_classes import RESULT_STATUS

from . import data_manager as datasvc
from . import runner_exp
from .dispatcher_modules.caches import _pending_parents, _sorted_task_groups, _unresolved_tasks

app_log = logger.app_log
log_stack_info = logger.log_stack_info
_global_status_queue = asyncio.Queue()
_status_queues = {}
_futures = {}

_global_event_listener = None

SYNC_DISPATCHES = get_config("dispatcher.use_async_dispatcher") == "false"


# Domain: dispatcher
async def _get_abstract_task_inputs(dispatch_id: str, node_id: int, node_name: str) -> dict:
    """Return placeholders for the required inputs for a task execution.

    Args:
        dispatch_id: id of the current dispatch
        node_id: Node id of this task in the transport graph.
        node_name: Name of the node.

    Returns: inputs: Input dictionary to be passed to the task with
        `node_id` placeholders for args, kwargs. These are to be
        resolved to their values later.
    """

    abstract_task_input = {"args": [], "kwargs": {}}

    for edge in await datasvc.get_incoming_edges(dispatch_id, node_id):

        parent = edge["source"]

        d = edge["attrs"]

        if d["edge_name"] != WAIT_EDGE_NAME:
            if d["param_type"] == "arg":
                abstract_task_input["args"].append((parent, d["arg_index"]))
            elif d["param_type"] == "kwarg":
                key = d["edge_name"]
                abstract_task_input["kwargs"][key] = parent

    sorted_args = sorted(abstract_task_input["args"], key=lambda x: x[1])
    abstract_task_input["args"] = [x[0] for x in sorted_args]

    return abstract_task_input


# Domain: dispatcher
async def _handle_completed_node(dispatch_id: str, node_id: int):

    next_task_groups = []
    app_log.debug(f"Node {node_id} completed")

    parent_gid = await datasvc.get_electron_attribute(dispatch_id, node_id, "task_group_id")
    for child in await datasvc.get_node_successors(dispatch_id, node_id):
        node_id = child["node_id"]
        gid = child["task_group_id"]
        app_log.debug(f"dispatch {dispatch_id}: parent gid {parent_gid}, child gid {gid}")
        if parent_gid != gid:
            await _pending_parents.decrement(dispatch_id, gid)
            now_pending = await _pending_parents.get_pending(dispatch_id, gid)
            if now_pending < 1:
                app_log.debug(f"Queuing task group {gid} for execution")
                next_task_groups.append(gid)

    return next_task_groups


# Domain: dispatcher
async def _handle_failed_node(dispatch_id: str, node_id: int):
    app_log.debug(f"Node {dispatch_id}:{node_id} failed")
    app_log.debug("8A: Failed node upsert statement (run_planned_workflow)")


# Domain: dispatcher
async def _handle_cancelled_node(dispatch_id: str, node_id: int):
    app_log.debug(f"Node {dispatch_id}:{node_id} cancelled")
    app_log.debug("9: Cancelled node upsert statement (run_planned_workflow)")


# Domain: dispatcher
async def _get_initial_tasks_and_deps(dispatch_id: str) -> Tuple[int, int, Dict]:
    """Compute the initial batch of tasks to submit and initialize each task's dep count

    Returns: (num_tasks, ready_nodes, pending_parents) where num_tasks is
        the total number of tasks in the graph, ready_nodes is the
        initial list of tasks to dispatch, and pending_parents is a map
        from `node_id` to the number of parents that have yet to
        complete.

    """

    # Number of pending predecessor nodes for each task group
    pending_parents = {}

    g_node_link = await datasvc.get_graph_nodes_links(dispatch_id)
    g = nx.readwrite.node_link_graph(g_node_link)

    # Topologically sort each task group
    sorted_task_groups = {}
    for node_id in nx.topological_sort(g):
        gid = g.nodes[node_id]["task_group_id"]
        if gid not in sorted_task_groups:
            sorted_task_groups[gid] = [node_id]
            pending_parents[gid] = 0
        else:
            sorted_task_groups[gid].append(node_id)

    for node_id in g.nodes:
        parent_gid = g.nodes[node_id]["task_group_id"]
        for succ, datadict in g.adj[node_id].items():
            child_gid = g.nodes[succ]["task_group_id"]
            n_edges = len(datadict.keys())
            if parent_gid != child_gid:
                pending_parents[child_gid] += n_edges

    initial_task_groups = [gid for gid, d in pending_parents.items() if d == 0]
    app_log.debug(f"Sorted task groups: {sorted_task_groups}")
    return initial_task_groups, pending_parents, sorted_task_groups


# Domain: dispatcher
async def _submit_task_group(dispatch_id: str, sorted_nodes: List[int], task_group_id: int):

    # Handle parameter nodes
    # Get name of the node for the current task
    node_name = await datasvc.get_electron_attribute(dispatch_id, sorted_nodes[0], "name")
    app_log.debug(f"7A: Node name: {node_name} (run_planned_workflow).")

    # Handle parameter nodes
    if node_name.startswith(parameter_prefix):

        if len(sorted_nodes) > 1:
            raise RuntimeError("Parameter nodes cannot be packed")

        app_log.debug("7C: Encountered parameter node {node_id}.")
        app_log.debug("8: Starting update node (run_planned_workflow).")

        node_result = {
            "node_id": sorted_nodes[0],
            "start_time": datetime.now(timezone.utc),
            "end_time": datetime.now(timezone.utc),
            "status": RESULT_STATUS.COMPLETED,
        }
        await datasvc.update_node_result(dispatch_id, node_result)
        app_log.debug("8A: Update node success (run_planned_workflow).")

    else:
        # Gather inputs for each task and send the task spec sequence to the runner
        task_specs = []
        known_nodes = []
        for node_id in sorted_nodes:
            app_log.debug(f"Gathering inputs for task {node_id} (run_planned_workflow).")

            abs_task_input = await _get_abstract_task_inputs(dispatch_id, node_id, node_name)

            selected_executor = await datasvc.get_electron_attribute(
                dispatch_id, node_id, "executor"
            )
            selected_executor_data = await datasvc.get_electron_attribute(
                dispatch_id, node_id, "executor_data"
            )
            task_spec = {
                "function_id": node_id,
                "name": node_name,
                "args_ids": abs_task_input["args"],
                "kwargs_ids": abs_task_input["kwargs"],
            }
            known_nodes += abs_task_input["args"]
            known_nodes += list(abs_task_input["kwargs"].values())
            task_specs.append(task_spec)

        app_log.debug(
            f"Submitting task group {dispatch_id}:{task_group_id} ({len(sorted_nodes)} tasks) to runner"
        )
        app_log.debug(f"Using new runner for task group {task_group_id}")

        known_nodes = list(set(known_nodes))
        coro = runner_exp.run_abstract_task_group(
            dispatch_id=dispatch_id,
            task_group_id=task_group_id,
            task_seq=task_specs,
            known_nodes=known_nodes,
            selected_executor=[selected_executor, selected_executor_data],
        )

        asyncio.create_task(coro)


async def _plan_workflow(dispatch_id: str) -> None:
    """
    Function to plan a workflow according to a schedule.
    Planning means to decide which executors (along with their arguments) will
    be used by each node.

    Args:
        dispatch_id: id of current dispatch

    Returns:
        None
    """

    pass


async def run_workflow(dispatch_id: str, wait: bool = SYNC_DISPATCHES) -> RESULT_STATUS:
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

    global _global_event_listener

    if not _global_event_listener:
        _global_event_listener = asyncio.create_task(_node_event_listener())

    result_info = await datasvc.get_dispatch_attributes(dispatch_id, ["status"])
    dispatch_status = result_info["status"]

    if dispatch_status == RESULT_STATUS.COMPLETED:
        datasvc.finalize_dispatch(dispatch_id)
        return RESULT_STATUS.COMPLETED

    try:
        await _plan_workflow(dispatch_id)

        if wait:
            fut = asyncio.Future()
            _futures[dispatch_id] = fut

        dispatch_status = await _submit_initial_tasks(dispatch_id)

        if wait:
            app_log.debug(f"Waiting for dispatch {dispatch_id}")
            dispatch_status = await fut
        else:
            app_log.debug(f"Running dispatch {dispatch_id} asynchronously")

    except Exception as ex:

        dispatch_status = await _handle_dispatch_exception(dispatch_id, ex)

    finally:
        if dispatch_status != RESULT_STATUS.RUNNING:
            datasvc.finalize_dispatch(dispatch_id)

    return dispatch_status


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
    # shared_var.set(str(RESULT_STATUS.CANCELLED))
    pass


def run_dispatch(dispatch_id: str) -> asyncio.Future:
    return asyncio.create_task(run_workflow(dispatch_id))


async def notify_node_status(
    dispatch_id: str, node_id: int, status: RESULT_STATUS, detail: Dict = {}
):
    msg = {
        "dispatch_id": dispatch_id,
        "node_id": node_id,
        "status": status,
        "detail": detail,
    }

    await _global_status_queue.put(msg)


async def _finalize_dispatch(dispatch_id: str):

    await _unresolved_tasks.remove(dispatch_id)
    app_log.debug(f"Removed unresolved counter for {dispatch_id}")

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
        status = RESULT_STATUS.FAILED if failed else RESULT_STATUS.CANCELLED
        result_update = datasvc.generate_dispatch_result(
            dispatch_id,
            status=status,
            error=error_msg,
            end_time=ts,
        )
        await datasvc.update_dispatch_result(dispatch_id, result_update)

    app_log.debug("8: All tasks finished running (run_planned_workflow)")

    app_log.debug("Workflow already postprocessed")

    result_info = await datasvc.get_dispatch_attributes(dispatch_id, ["status"])
    return result_info["status"]


async def _initialize_caches(dispatch_id, pending_parents, sorted_task_groups):
    for gid, indegree in pending_parents.items():
        await _pending_parents.set_pending(dispatch_id, gid, indegree)

    for gid, sorted_nodes in sorted_task_groups.items():
        await _sorted_task_groups.set_task_group(dispatch_id, gid, sorted_nodes)

    await _unresolved_tasks.set_unresolved(dispatch_id, 0)


async def _submit_initial_tasks(dispatch_id: str):
    app_log.debug("3: Inside run_planned_workflow (run_planned_workflow).")
    dispatch_result = datasvc.generate_dispatch_result(
        dispatch_id, start_time=datetime.now(timezone.utc), status=RESULT_STATUS.RUNNING
    )
    await datasvc.update_dispatch_result(dispatch_id, dispatch_result)

    app_log.debug(f"4: Workflow status changed to running {dispatch_id} (run_planned_workflow).")
    app_log.debug("5: Wrote lattice status to DB (run_planned_workflow).")

    initial_groups, pending_parents, sorted_task_groups = await _get_initial_tasks_and_deps(
        dispatch_id
    )

    await _initialize_caches(dispatch_id, pending_parents, sorted_task_groups)

    for gid in initial_groups:
        sorted_nodes = sorted_task_groups[gid]
        app_log.debug(f"Sorted nodes group group {gid}: {sorted_nodes}")
        await _unresolved_tasks.increment(dispatch_id, len(sorted_nodes))
        await _submit_task_group(dispatch_id, sorted_nodes, gid)

    return RESULT_STATUS.RUNNING


async def _handle_node_status_update(dispatch_id, node_id, node_status, detail):

    app_log.debug(f"Received node status update {node_id}: {node_status}")

    if node_status == RESULT_STATUS.RUNNING:
        return

    if node_status == RESULT_STATUS.DISPATCHING:
        sub_dispatch_id = detail["sub_dispatch_id"]
        run_dispatch(sub_dispatch_id)
        app_log.debug(f"Running sublattice dispatch {sub_dispatch_id}")

        return

    # Terminal node statuses
    await _unresolved_tasks.decrement(dispatch_id)

    if node_status == RESULT_STATUS.COMPLETED:
        next_task_groups = await _handle_completed_node(dispatch_id, node_id)
        for gid in next_task_groups:
            sorted_nodes = await _sorted_task_groups.get_task_group(dispatch_id, gid)
            await _unresolved_tasks.increment(dispatch_id, len(sorted_nodes))
            await _submit_task_group(dispatch_id, sorted_nodes, gid)
        return

    if node_status == RESULT_STATUS.FAILED:
        await _handle_failed_node(dispatch_id, node_id)
        return

    if node_status == RESULT_STATUS.CANCELLED:
        await _handle_cancelled_node(dispatch_id, node_id)
        return


async def _handle_dispatch_exception(dispatch_id: str, ex: Exception) -> RESULT_STATUS:
    error_msg = "".join(traceback.TracebackException.from_exception(ex).format())
    app_log.exception(f"Exception during _run_planned_workflow: {error_msg}")

    dispatch_result = datasvc.generate_dispatch_result(
        dispatch_id,
        end_time=datetime.now(timezone.utc),
        status=RESULT_STATUS.FAILED,
        error=error_msg,
    )

    await datasvc.update_dispatch_result(dispatch_id, dispatch_result)
    return RESULT_STATUS.FAILED


# msg = {
#     "dispatch_id": dispatch_id,
#     "node_id": node_id,
#     "status": status,
#     "detail": detail,
# }
async def _node_event_listener():
    app_log.debug("Starting event listener")
    while True:
        msg = await _global_status_queue.get()

        asyncio.create_task(_handle_event(msg))


async def _handle_event(msg: Dict):
    dispatch_id = msg["dispatch_id"]
    node_id = msg["node_id"]
    node_status = msg["status"]
    detail = msg["detail"]

    try:
        await _handle_node_status_update(dispatch_id, node_id, node_status, detail)

    except Exception as ex:
        dispatch_status = await _handle_dispatch_exception(dispatch_id, ex)
        await datasvc.persist_result(dispatch_id)
        fut = _futures.get(dispatch_id, None)
        if fut:
            fut.set_result(dispatch_status)
        return dispatch_status

    unresolved = await _unresolved_tasks.get_unresolved(dispatch_id)
    if unresolved < 1:
        app_log.debug("Finalizing dispatch")
        try:
            dispatch_status = await _finalize_dispatch(dispatch_id)
        except Exception as ex:
            dispatch_status = await _handle_dispatch_exception(dispatch_id, ex)

        finally:
            await datasvc.persist_result(dispatch_id)
            fut = _futures.get(dispatch_id, None)
            if fut:
                fut.set_result(dispatch_status)

        return dispatch_status
