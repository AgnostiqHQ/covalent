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
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from functools import partial
from threading import Lock
from typing import Any, Dict, List, Tuple

import uvloop
from sqlalchemy import update
from sqlalchemy.orm import Session

from covalent import dispatch
from covalent._data_store.datastore import workflow_db
from covalent._data_store.models import Lattice as Lattice_model
from covalent._results_manager import Result
from covalent._results_manager.write_result_to_db import (
    update_lattices_data,
    write_lattice_error,
    write_sublattice_electron_id,
)
from covalent._shared_files import logger
from covalent._shared_files.context_managers import active_lattice_manager
from covalent._shared_files.defaults import (
    electron_dict_prefix,
    electron_list_prefix,
    parameter_prefix,
    prefix_separator,
    sublattice_prefix,
)
from covalent._workflow import DepsBash, DepsCall, DepsPip
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import TransportableObject
from covalent.executor import _executor_manager
from covalent.executor.base import BaseAsyncExecutor, wrapper_fn
from covalent_ui import result_webhook

from .._db.dispatchdb import DispatchDB
from ..entry_point import futures

app_log = logger.app_log
log_stack_info = logger.log_stack_info


# This is to be run out-of-process
def _dispatch(fn, *args, **kwargs):
    return dispatch(fn)(*args, **kwargs)


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
        task_input = {"args": [], "kwargs": {"x": TransportableObject.make_transportable(values)}}
    elif node_name.startswith(electron_dict_prefix):
        values = {}
        for parent in result_object.lattice.transport_graph.get_dependencies(node_id):

            edge_data = result_object.lattice.transport_graph.get_edge_data(parent, node_id)

            value = result_object.lattice.transport_graph.get_node_value(parent, "output")
            for e_key, d in edge_data.items():
                key = d["edge_name"]
                values[key] = value

        task_input = {"args": [], "kwargs": {"x": TransportableObject.make_transportable(values)}}
    else:
        task_input = {"args": [], "kwargs": {}}

        for parent in result_object.lattice.transport_graph.get_dependencies(node_id):

            edge_data = result_object.lattice.transport_graph.get_edge_data(parent, node_id)
            value = result_object.lattice.transport_graph.get_node_value(parent, "output")

            for e_key, d in edge_data.items():
                if not d.get("wait_for"):
                    if d["param_type"] == "arg":
                        task_input["args"].append((value, d["arg_index"]))
                    elif d["param_type"] == "kwarg":
                        key = d["edge_name"]
                        task_input["kwargs"][key] = value

        sorted_args = sorted(task_input["args"], key=lambda x: x[1])
        task_input["args"] = [x[0] for x in sorted_args]

    return task_input


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


async def _dispatch_sublattice(
    dispatch_id: str,
    results_dir: str,
    inputs: Dict,
    serialized_callable: Any,
    tasks_pool: ThreadPoolExecutor,
    workflow_executor: Any,
) -> str:
    """Dispatch a sublattice using the workflow_executor."""

    try:
        short_name, object_dict = workflow_executor

        if short_name == "client":
            raise RuntimeError("No executor selected for dispatching sublattices")

    except Exception as ex:
        app_log.debug(f"Exception when trying to determine sublattice executor: {ex}")
        raise ex

    sub_dispatch_inputs = {"args": [serialized_callable], "kwargs": inputs["kwargs"]}
    for arg in inputs["args"]:
        sub_dispatch_inputs["args"].append(arg)

    # Dispatch the sublattice workflow. This must be run
    # externally since it involves deserializing the
    # sublattice workflow function.
    fut = asyncio.create_task(
        _run_task(
            node_id=-1,
            dispatch_id=dispatch_id,
            results_dir=results_dir,
            serialized_callable=TransportableObject.make_transportable(_dispatch),
            selected_executor=workflow_executor,
            node_name="dispatch_sublattice",
            call_before=[],
            call_after=[],
            inputs=sub_dispatch_inputs,
            tasks_pool=tasks_pool,
            workflow_executor=workflow_executor,
        )
    )

    res = await fut
    return json.loads(res["output"].json)


async def _run_task(
    node_id: int,
    dispatch_id: str,
    results_dir: str,
    inputs: Dict,
    serialized_callable: Any,
    selected_executor: Any,
    call_before: List,
    call_after: List,
    node_name: str,
    tasks_pool: ThreadPoolExecutor,
    workflow_executor: Any,
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

    # Instantiate the executor from JSON
    try:
        short_name, object_dict = selected_executor

        app_log.debug(f"Running task {node_name} using executor {short_name}, {object_dict}")

        # the executor is determined during scheduling and provided in the execution metadata
        executor = _executor_manager.get_executor(short_name)
        executor.from_dict(object_dict)
    except Exception as ex:
        app_log.debug(f"Exception when trying to determine executor: {ex}")
        raise ex

    # run the task on the executor and register any failures
    try:

        if node_name.startswith(sublattice_prefix):
            sub_dispatch_id = await _dispatch_sublattice(
                dispatch_id=dispatch_id,
                results_dir=results_dir,
                inputs=inputs,
                serialized_callable=serialized_callable,
                tasks_pool=tasks_pool,
                workflow_executor=workflow_executor,
            )

            app_log.debug(f"Sublattice dispatch id: {sub_dispatch_id}")

            write_sublattice_electron_id(
                parent_dispatch_id=dispatch_id,
                sublattice_node_id=node_id,
                sublattice_dispatch_id=sub_dispatch_id,
            )
            # Read the result object directly from the server

            sublattice_result = futures[sub_dispatch_id].result()

            if not sublattice_result:
                raise RuntimeError("Sublattice execution failed")

            output = sublattice_result.encoded_result
            end_time = datetime.now(timezone.utc)
            node_result = generate_node_result(
                node_id=node_id,
                end_time=end_time,
                status=Result.COMPLETED,
                output=output,
                sublattice_result=sublattice_result,
            )

            app_log.debug("Sublattice dispatched (run_task)")
            # Don't continue unless sublattice finishes
            if sublattice_result.status != Result.COMPLETED:
                node_result["status"] = Result.FAILED
                node_result["error"] = "Sublattice workflow failed to complete"

                sublattice_result.upsert_lattice_data()

        else:
            app_log.debug(f"Executing task {node_name}")

            assembled_callable = partial(wrapper_fn, serialized_callable, call_before, call_after)

            execute_callable = partial(
                executor.execute,
                function=assembled_callable,
                args=inputs["args"],
                kwargs=inputs["kwargs"],
                dispatch_id=dispatch_id,
                results_dir=results_dir,
                node_id=node_id,
            )

            if isinstance(executor, BaseAsyncExecutor):
                output, stdout, stderr = await execute_callable()
            else:
                loop = asyncio.get_running_loop()
                output, stdout, stderr = await loop.run_in_executor(tasks_pool, execute_callable)

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

        app_log.error(f"Exception occurred when running task {node_id}: {ex}")

        node_result = generate_node_result(
            node_id=node_id,
            end_time=end_time,
            status=Result.FAILED,
            error="".join(traceback.TracebackException.from_exception(ex).format()),
        )
        app_log.exception("Run task exception")
    app_log.debug("Returning node result (run_task)")

    return node_result


def _gather_deps(result_object: Result, node_id: int) -> Tuple[List, List]:
    """Assemble deps for a node into the final call_before and call_after"""

    deps = result_object.lattice.transport_graph.get_node_value(node_id, "metadata")["deps"]

    # Assemble call_before and call_after from all the deps

    call_before_objs_json = result_object.lattice.transport_graph.get_node_value(
        node_id, "metadata"
    )["call_before"]
    call_after_objs_json = result_object.lattice.transport_graph.get_node_value(
        node_id, "metadata"
    )["call_after"]

    call_before = []
    call_after = []

    # Rehydrate deps from JSON
    if "bash" in deps:
        dep = DepsBash()
        dep.from_dict(deps["bash"])
        call_before.append(dep.apply())

    if "pip" in deps:
        dep = DepsPip()
        dep.from_dict(deps["pip"])
        call_before.append(dep.apply())

    for dep_json in call_before_objs_json:
        dep = DepsCall()
        dep.from_dict(dep_json)
        call_before.append(dep.apply())

    for dep_json in call_after_objs_json:
        dep = DepsCall()
        dep.from_dict(dep_json)
        call_after.append(dep.apply())

    return call_before, call_after


async def _handle_completed_node(result_object, node_result, pending_deps, tasks_queue):
    g = result_object.lattice.transport_graph._graph

    for child, edges in g.adj[node_result["node_id"]].items():
        for edge in edges:
            pending_deps[child] -= 1
        if pending_deps[child] < 1:
            app_log.debug(f"Queuing node {child} for execution")
            await tasks_queue.put(child)


async def _handle_failed_node(result_object, node_result, pending_deps, tasks_queue):
    node_id = node_result["node_id"]
    result_object._status = Result.FAILED
    result_object._end_time = datetime.now(timezone.utc)
    result_object._error = f"Node {result_object._get_node_name(node_id)} failed: \n{result_object._get_node_error(node_id)}"
    app_log.warning("8A: Failed node upsert statement (run_planned_workflow)")
    result_object.upsert_lattice_data()
    result_webhook.send_update(result_object)
    await tasks_queue.put(-1)


async def _handle_cancelled_node(result_object, node_result, pending_deps, tasks_queue):
    result_object._status = Result.CANCELLED
    result_object._end_time = datetime.now(timezone.utc)
    app_log.warning("9: Failed node upsert statement (run_planned_workflow)")
    result_object.upsert_lattice_data()
    result_webhook.send_update(result_object)
    await tasks_queue.put(-1)


async def _update_node_result(lock, result_object, node_result, pending_deps, tasks_queue):
    with lock:
        app_log.warning("Updating node result (run_planned_workflow).")
        result_object._update_node(**node_result)
        result_webhook.send_update(result_object)

        node_status = node_result["status"]
        if node_status == Result.COMPLETED:
            await _handle_completed_node(result_object, node_result, pending_deps, tasks_queue)
            return

        if node_status == Result.FAILED:
            await _handle_failed_node(result_object, node_result, pending_deps, tasks_queue)
            return

        if node_status == Result.CANCELLED:
            await _handle_cancelled_node(result_object, node_result, pending_deps, tasks_queue)
            return

        if node_status == Result.RUNNING:
            return


async def _run_task_and_update(run_task_callable, lock, result_object, pending_deps, tasks_queue):
    node_result = await run_task_callable()

    # NOTE: This is a blocking operation because of db writes and needs special handling when
    # we switch to an event loop for processing tasks
    await _update_node_result(lock, result_object, node_result, pending_deps, tasks_queue)
    return node_result


async def _initialize_deps_and_queue(
    result_object: Result, tasks_queue: Queue, pending_deps: dict
) -> int:
    """Initialize the data structures controlling when tasks are queued for execution.

    Returns the total number of nodes in the transport graph."""

    num_tasks = 0
    g = result_object.lattice.transport_graph._graph
    for node_id, d in g.in_degree():
        app_log.debug(f"Node {node_id} has {d} parents")

        pending_deps[node_id] = d
        num_tasks += 1
        if d == 0:
            await tasks_queue.put(node_id)

    return num_tasks


async def _postprocess_workflow(result_object: Result, thread_pool: ThreadPoolExecutor) -> Result:
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
    result_object.upsert_lattice_data()

    app_log.debug(f"Preparing to post-process workflow {result_object.dispatch_id}")

    if pp_executor == "client":
        app_log.debug("Workflow to be postprocessed client side")
        result_object._status = Result.PENDING_POSTPROCESSING
        result_object._end_time = datetime.now(timezone.utc)
        result_object.upsert_lattice_data()
        result_webhook.send_update(result_object)
        return result_object

    post_processing_inputs = {}
    post_processing_inputs["args"] = [
        TransportableObject.make_transportable(result_object.lattice),
        TransportableObject.make_transportable(result_object.get_all_node_outputs()),
    ]
    post_processing_inputs["kwargs"] = {}

    try:
        future = asyncio.create_task(
            _run_task(
                node_id=-1,
                dispatch_id=result_object.dispatch_id,
                results_dir=result_object.results_dir,
                serialized_callable=TransportableObject(_post_process),
                selected_executor=post_processor,
                node_name="post_process",
                call_before=[],
                call_after=[],
                inputs=post_processing_inputs,
                tasks_pool=thread_pool,
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
        result_object.upsert_lattice_data()
        result_webhook.send_update(result_object)

        return result_object

    if post_process_result["status"] != Result.COMPLETED:
        err = post_process_result["stderr"]
        app_log.debug(f"Post-processing failed: {err}")
        result_object._status = Result.POSTPROCESSING_FAILED
        result_object._error = f"Post-processing failed: {err}"
        result_object._end_time = datetime.now(timezone.utc)
        result_object.upsert_lattice_data()
        result_webhook.send_update(result_object)

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


async def _run_planned_workflow(result_object: Result, thread_pool: ThreadPoolExecutor) -> Result:
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

    app_log.debug("3: Inside run_planned_workflow (run_planned_workflow).")

    tasks_queue = Queue()
    pending_deps = {}
    lock = Lock()
    task_futures: list = []

    app_log.debug(
        f"4: Workflow status changed to running {result_object.dispatch_id} (run_planned_workflow)."
    )

    result_object._status = Result.RUNNING
    result_object._start_time = datetime.now(timezone.utc)

    with workflow_db.session() as session:
        session.execute(
            update(Lattice_model)
            .where(Lattice_model.dispatch_id == result_object.dispatch_id)
            .values(
                status=str(Result.RUNNING),
                updated_at=datetime.now(timezone.utc),
                started_at=datetime.now(timezone.utc),
            )
        )
        session.commit()
    app_log.debug("5: Wrote lattice status to DB (run_planned_workflow).")

    # Executor for post_processing and dispatching sublattices
    pp_executor = result_object.lattice.get_metadata("workflow_executor")
    pp_executor_data = result_object.lattice.get_metadata("workflow_executor_data")
    post_processor = [pp_executor, pp_executor_data]

    tasks_left = await _initialize_deps_and_queue(result_object, tasks_queue, pending_deps)

    while tasks_left > 0:
        app_log.debug(f"{tasks_left} tasks left")

        tasks_left -= 1
        node_id = await tasks_queue.get()
        app_log.debug(f"Processing node {node_id}")

        if node_id < 0:
            app_log.debug(f"Workflow {result_object.dispatch_id} failed or cancelled.")
            await asyncio.gather(*task_futures)
            return result_object

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
            await _update_node_result(lock, result_object, node_result, pending_deps, tasks_queue)
            app_log.debug("8A: Update node success (run_planned_workflow).")

            continue

        # Gather inputs and dispatch task
        app_log.debug(f"Gathering inputs for task {node_id} (run_planned_workflow).")
        task_input = _get_task_inputs(node_id, node_name, result_object)

        start_time = datetime.now(timezone.utc)
        serialized_callable = result_object.lattice.transport_graph.get_node_value(
            node_id, "function"
        )

        selected_executor = result_object.lattice.transport_graph.get_node_value(
            node_id, "metadata"
        )["executor"]

        selected_executor_data = result_object.lattice.transport_graph.get_node_value(
            node_id, "metadata"
        )["executor_data"]

        app_log.debug(f"Collecting deps for task {node_id}")
        try:
            call_before, call_after = _gather_deps(result_object, node_id)

        except Exception as ex:
            app_log.error(f"Exception when trying to collect deps: {ex}")
            raise ex

        node_result = generate_node_result(
            node_id=node_id,
            start_time=start_time,
            status=Result.RUNNING,
        )
        await _update_node_result(lock, result_object, node_result, pending_deps, tasks_queue)
        app_log.debug("7: Updating nodes after deps (run_planned_workflow)")

        app_log.debug(f"Submitting task {node_id} to executor")

        run_task_callable = partial(
            _run_task,
            node_id=node_id,
            dispatch_id=result_object.dispatch_id,
            results_dir=result_object.results_dir,
            serialized_callable=serialized_callable,
            selected_executor=[selected_executor, selected_executor_data],
            node_name=node_name,
            call_before=call_before,
            call_after=call_after,
            inputs=task_input,
            tasks_pool=thread_pool,
            workflow_executor=post_processor,
        )

        # Add the task generated for the node to the list of tasks
        future = asyncio.create_task(
            _run_task_and_update(
                run_task_callable=run_task_callable,
                lock=lock,
                result_object=result_object,
                pending_deps=pending_deps,
                tasks_queue=tasks_queue,
            )
        )

        task_futures.append(future)

    await asyncio.gather(*task_futures)

    if result_object._status in [Result.FAILED, Result.CANCELLED]:
        app_log.debug(f"Workflow {result_object.dispatch_id} cancelled or failed")
        return result_object

    app_log.debug("8: All tasks finished running (run_planned_workflow)")

    result_object = await _postprocess_workflow(result_object, thread_pool)

    result_object.persist()
    result_webhook.send_update(result_object)

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


def run_workflow(result_object: Result, tasks_pool: ThreadPoolExecutor) -> Result:
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
        uvloop.install()
        result_object = asyncio.run(_run_planned_workflow(result_object, tasks_pool))

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
