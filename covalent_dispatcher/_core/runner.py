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
Defines the core functionality of the runner
"""

import asyncio
import json
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from functools import partial
from typing import Any, Dict, List, Literal, Tuple, Union

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.context_managers import active_lattice_manager
from covalent._shared_files.defaults import prefix_separator, sublattice_prefix
from covalent._workflow import DepsBash, DepsCall, DepsPip
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import TransportableObject
from covalent.executor import _executor_manager
from covalent.executor.base import wrapper_fn

from .._db import upsert
from .._db.write_result_to_db import get_sublattice_electron_id
from . import data_manager as datasvc
from . import dispatcher
from .data_modules.job_manager import get_jobs_metadata, set_cancel_result
from .runner_modules import executor_proxy

app_log = logger.app_log
log_stack_info = logger.log_stack_info
debug_mode = get_config("sdk.log_level") == "debug"

_cancel_threadpool = ThreadPoolExecutor()


# This is to be run out-of-process
def _build_sublattice_graph(sub: Lattice, parent_metadata: Dict, *args, **kwargs):
    """
    Build the sublattice graph dynamically

    Arg(s)
        sub: Lattice associated with the sub-lattice
        parent_metadata: Metadata of the parent lattice

    Return(s)
        JSON representation of the sublattice transport graph
    """
    for k in sub.metadata.keys():
        if not sub.metadata[k]:
            sub.metadata[k] = parent_metadata[k]

    sub.build_graph(*args, **kwargs)
    return sub.serialize_to_json()


async def _dispatch_sublattice(
    parent_result_object: Result,
    parent_node_id: int,
    parent_electron_id: int,
    inputs: Dict,
    serialized_callable: Any,
    workflow_executor: Any,
) -> str:
    """Dispatch a sublattice using the workflow_executor."""

    app_log.debug("Inside _dispatch_sublattice")

    try:
        short_name, object_dict = workflow_executor

        if short_name == "client":
            app_log.error("No executor selected for dispatching sublattices")
            raise RuntimeError("No executor selected for dispatching sublattices")

    except Exception as ex:
        app_log.debug(f"Exception when trying to determine sublattice executor: {ex}")
        raise ex

    parent_metadata = TransportableObject.make_transportable(parent_result_object.lattice.metadata)
    sub_dispatch_inputs = {
        "args": [serialized_callable, parent_metadata],
        "kwargs": inputs["kwargs"],
    }
    for arg in inputs["args"]:
        sub_dispatch_inputs["args"].append(arg)

    # Build the sublattice graph. This must be run
    # externally since it involves deserializing the
    # sublattice workflow function.
    res = await _run_task(
        result_object=parent_result_object,
        node_id=parent_node_id,
        serialized_callable=TransportableObject.make_transportable(_build_sublattice_graph),
        selected_executor=workflow_executor,
        node_name="build_sublattice_graph",
        call_before=[],
        call_after=[],
        inputs=sub_dispatch_inputs,
        workflow_executor=workflow_executor,
    )

    if res["status"] == Result.COMPLETED:
        json_sublattice = json.loads(res["output"].json)

        sub_dispatch_id = datasvc.make_dispatch(
            json_sublattice, parent_result_object, parent_electron_id
        )
        app_log.debug(f"Sublattice dispatch id: {sub_dispatch_id}")
        return sub_dispatch_id
    else:
        app_log.debug("Error building sublattice graph")
        stderr = res["stderr"]
        raise RuntimeError(f"Error building sublattice graph: {stderr}")


# Domain: runner
# to be called by _run_abstract_task
def _get_task_input_values(result_object: Result, abs_task_inputs: dict) -> dict:
    """
    Retrive the input values from the result_object for the task

    Arg(s)
        result_object: Result object of the workflow
        abs_task_inputs: Task inputs dictionary

    Return(s)
        node_values: Dictionary of task inputs
    """
    node_values = {}
    args = abs_task_inputs["args"]
    for node_id in args:
        value = result_object.lattice.transport_graph.get_node_value(node_id, "output")
        node_values[node_id] = value

    kwargs = abs_task_inputs["kwargs"]
    for _, node_id in kwargs.items():
        value = result_object.lattice.transport_graph.get_node_value(node_id, "output")
        node_values[node_id] = value

    return node_values


# Domain: runner
async def _run_abstract_task(
    dispatch_id: str,
    node_id: int,
    node_name: str,
    abstract_inputs: Dict,
    selected_executor: Any,
    workflow_executor: Any,
) -> None:
    # Resolve abstract task and inputs to their concrete (serialized) values
    result_object = datasvc.get_result_object(dispatch_id)
    timestamp = datetime.now(timezone.utc)

    try:
        cancel_req = await _get_cancel_requested(dispatch_id, node_id)
        if cancel_req:
            app_log.debug(f"Don't run cancelled task {dispatch_id}:{node_id}")
            return datasvc.generate_node_result(
                node_id=node_id,
                start_time=timestamp,
                end_time=timestamp,
                status=Result.CANCELLED,
            )
        serialized_callable = result_object.lattice.transport_graph.get_node_value(
            node_id, "function"
        )
        input_values = _get_task_input_values(result_object, abstract_inputs)

        abstract_args = abstract_inputs["args"]
        abstract_kwargs = abstract_inputs["kwargs"]
        args = [input_values[node_id] for node_id in abstract_args]
        kwargs = {k: input_values[v] for k, v in abstract_kwargs.items()}
        task_input = {"args": args, "kwargs": kwargs}

        app_log.debug(f"Collecting deps for task {node_id}")

        call_before, call_after = _gather_deps(result_object, node_id)

    except Exception as ex:
        app_log.error(f"Exception when trying to resolve inputs or deps: {ex}")
        node_result = datasvc.generate_node_result(
            node_id=node_id,
            start_time=timestamp,
            end_time=timestamp,
            status=Result.FAILED,
            error=str(ex),
        )
        return node_result

    node_result = datasvc.generate_node_result(
        node_id=node_id,
        start_time=timestamp,
        status=Result.RUNNING,
    )
    app_log.debug(f"7: Marking node {node_id} as running (_run_abstract_task)")

    await datasvc.update_node_result(result_object, node_result)

    return await _run_task(
        result_object=result_object,
        node_id=node_id,
        serialized_callable=serialized_callable,
        selected_executor=selected_executor,
        node_name=node_name,
        call_before=call_before,
        call_after=call_after,
        inputs=task_input,
        workflow_executor=workflow_executor,
    )


# Domain: runner
async def _run_task(
    result_object: Result,
    node_id: int,
    inputs: Dict,
    serialized_callable: Any,
    selected_executor: Any,
    call_before: List,
    call_after: List,
    node_name: str,
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

    dispatch_id = result_object.dispatch_id
    results_dir = result_object.results_dir

    # Instantiate the executor from JSON
    try:
        short_name, object_dict = selected_executor

        app_log.debug(f"Running task {node_name} using executor {short_name}, {object_dict}")

        # the executor is determined during scheduling and provided in the execution metadata
        executor = _executor_manager.get_executor(short_name)
        executor.from_dict(object_dict)
        executor._init_runtime(loop=asyncio.get_running_loop())
    except Exception as ex:
        tb = "".join(traceback.TracebackException.from_exception(ex).format())
        app_log.debug("Exception when trying to instantiate executor:")
        app_log.debug(tb)
        error_msg = tb if debug_mode else str(ex)
        node_result = datasvc.generate_node_result(
            node_id=node_id,
            end_time=datetime.now(timezone.utc),
            status=Result.FAILED,
            error=error_msg,
        )
        return node_result

    # run the task on the executor and register any failures
    try:
        if node_name.startswith(sublattice_prefix):
            sub_electron_id = get_sublattice_electron_id(
                parent_dispatch_id=dispatch_id, sublattice_node_id=node_id
            )

            sub_dispatch_id = await _dispatch_sublattice(
                parent_result_object=result_object,
                parent_node_id=node_id,
                parent_electron_id=sub_electron_id,
                inputs=inputs,
                serialized_callable=serialized_callable,
                workflow_executor=workflow_executor,
            )

            node_result = datasvc.generate_node_result(
                node_id=node_id,
                sub_dispatch_id=sub_dispatch_id,
            )

            dispatcher.run_dispatch(sub_dispatch_id)
            app_log.debug(f"Running sublattice dispatch {sub_dispatch_id}")

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

            asyncio.create_task(executor_proxy.watch(dispatch_id, node_id, executor))

            output, stdout, stderr, status = await executor._execute(
                function=assembled_callable,
                args=inputs["args"],
                kwargs=inputs["kwargs"],
                dispatch_id=dispatch_id,
                results_dir=results_dir,
                node_id=node_id,
            )

            node_result = datasvc.generate_node_result(
                node_id=node_id,
                end_time=datetime.now(timezone.utc),
                status=status,
                output=output,
                stdout=stdout,
                stderr=stderr,
            )

    except Exception as ex:
        tb = "".join(traceback.TracebackException.from_exception(ex).format())
        app_log.debug(f"Exception occurred when running task {node_id}:")
        app_log.debug(tb)
        error_msg = tb if debug_mode else str(ex)
        node_result = datasvc.generate_node_result(
            node_id=node_id,
            end_time=datetime.now(timezone.utc),
            status=Result.FAILED,
            error=error_msg,
        )
    app_log.debug(f"Node result: {node_result}")
    return node_result


# Domain: runner
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


# Domain: runner
async def run_abstract_task(
    dispatch_id: str,
    node_id: int,
    node_name: str,
    abstract_inputs: Dict,
    selected_executor: Any,
    workflow_executor: Any,
) -> None:
    node_result = await _run_abstract_task(
        dispatch_id=dispatch_id,
        node_id=node_id,
        node_name=node_name,
        abstract_inputs=abstract_inputs,
        selected_executor=selected_executor,
        workflow_executor=workflow_executor,
    )
    result_object = datasvc.get_result_object(dispatch_id)
    await datasvc.update_node_result(result_object, node_result)


# Domain: runner
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


# Domain: runner
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
    upsert.lattice_data(result_object)

    app_log.debug(f"Preparing to post-process workflow {result_object.dispatch_id}")

    if pp_executor == "client":
        app_log.debug("Workflow to be postprocessed client side")
        result_object._status = Result.PENDING_POSTPROCESSING
        result_object._end_time = datetime.now(timezone.utc)
        upsert.lattice_data(result_object)
        return result_object

    post_processing_inputs = {}
    post_processing_inputs["args"] = [
        TransportableObject.make_transportable(result_object.lattice),
        TransportableObject.make_transportable(result_object.get_all_node_outputs()),
    ]
    post_processing_inputs["kwargs"] = {}

    app_log.debug(f"Submitted post-processing job to executor {post_processor}")
    post_process_result = await _run_task(
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

    if post_process_result["status"] != Result.COMPLETED:
        stderr = post_process_result["stderr"] if post_process_result["stderr"] else ""
        err = post_process_result["error"] if post_process_result["error"] else ""
        error_msg = stderr + err

        app_log.debug(f"Post-processing failed: {err}")
        result_object._status = Result.POSTPROCESSING_FAILED
        result_object._error = f"Post-processing failed: {error_msg}"
        result_object._end_time = datetime.now(timezone.utc)
        upsert.lattice_data(result_object)

        app_log.debug("Returning from _postprocess_workflow")
        return result_object

    result_object._result = post_process_result["output"]
    result_object._status = Result.COMPLETED
    result_object._end_time = datetime.now(timezone.utc)

    app_log.debug(
        f"10: Successfully post-processed result {result_object.dispatch_id} (run_planned_workflow)"
    )

    return result_object


async def postprocess_workflow(dispatch_id: str) -> Result:
    """
    Public facing `postprocess_workflow`

    Arg(s)
        dispatch_id: Unique identifier for dispatched workflow

    Return(s)
        result_object: Result object of the workflow
    """
    result_object = datasvc.get_result_object(dispatch_id)
    return await _postprocess_workflow(result_object)


async def _cancel_task(
    dispatch_id: str, task_id: int, executor, executor_data: Dict, job_handle: str
) -> Union[Any, Literal[False]]:
    """
    Cancel the task currently being executed by the executor

    Arg(s)
        dispatch_id: Dispatch ID
        task_id: Task ID of the electron in transport graph to be cancelled
        executor: Covalent executor currently being used to execute the task
        executor_data: Executor configuration arguments
        job_handle: Unique identifier assigned to the task by the backend running the job

    Return(s)
        cancel_job_result: Status of the job cancellation action
    """
    app_log.debug(f"Cancel task {task_id} using executor {executor}, {executor_data}")
    app_log.debug(f"job_handle: {job_handle}")

    try:
        executor = _executor_manager.get_executor(executor)
        executor.from_dict(executor_data)
        executor._init_runtime(loop=asyncio.get_running_loop(), cancel_pool=_cancel_threadpool)

        task_metadata = {"dispatch_id": dispatch_id, "node_id": task_id}

        cancel_job_result = await executor._cancel(task_metadata, json.loads(job_handle))
    except Exception as ex:
        app_log.debug(f"Execption when cancel task {dispatch_id}:{task_id}: {ex}")
        cancel_job_result = False

    await set_cancel_result(dispatch_id, task_id, cancel_job_result)
    return cancel_job_result


def to_cancel_kwargs(
    index: int, node_id: int, node_metadata: List[dict], job_metadata: List[dict]
) -> dict:
    """
    Convert node_metadata for a given node `node_id` into a dictionary

    Arg(s)
        index: Index into the node_metadata list
        node_id: Node ID
        node_metadata: List of node metadata attributes
        job_metadata: List of metadata for the current job

    Return(s)
        Node metadata dictionary
    """
    return {
        "task_id": node_id,
        "executor": node_metadata[index]["executor"],
        "executor_data": node_metadata[index]["executor_data"],
        "job_handle": job_metadata[index]["job_handle"],
    }


async def cancel_tasks(dispatch_id: str, task_ids: List[int]) -> None:
    """
    Request all tasks with `task_ids` to be cancelled in the workflow identified by `dispatch_id`

    Arg(s)
        dispatch_id: Dispatch ID of the workflow
        task_ids: List of task ids to be cancelled

    Return(s)
        None
    """
    job_metadata = await get_jobs_metadata(dispatch_id, task_ids)
    node_metadata = _get_metadata_for_nodes(dispatch_id, task_ids)

    cancel_task_kwargs = [
        to_cancel_kwargs(i, x, node_metadata, job_metadata) for i, x in enumerate(task_ids)
    ]

    for kwargs in cancel_task_kwargs:
        asyncio.create_task(_cancel_task(dispatch_id, **kwargs))


def _get_metadata_for_nodes(dispatch_id: str, node_ids: list) -> List[Any]:
    """
    Returns all the metadata associated with the node(s) for the workflow identified by `dispatch_id`

    Arg(s)
        dispatch_id: Dispatch ID of the workflow
        node_ids: List of node ids from the workflow to retrive the metadata for

    Return(s)
        List of node metadata for the given `node_ids`
    """
    res = datasvc.get_result_object(dispatch_id)
    tg = res.lattice.transport_graph
    return list(map(lambda x: tg.get_node_value(x, "metadata"), node_ids))


async def _get_cancel_requested(dispatch_id: str, task_id: int) -> Any:
    """
    Query if a specific task has been requested to be cancelled

    Arg(s)
        dispatch_id: Dispatch ID of the workflow
        task_id: ID of the node to be cancelled

    Return(s)
        Whether the task has been requested to be cancelled or not
    """
    records = await get_jobs_metadata(dispatch_id, [task_id])
    return records[0]["cancel_requested"]
