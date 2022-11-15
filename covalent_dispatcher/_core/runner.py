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
from datetime import datetime, timezone
from functools import partial
from typing import Any, Dict, List, Tuple

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.context_managers import active_lattice_manager
from covalent._shared_files.defaults import prefix_separator, sublattice_prefix
from covalent._workflow import DepsBash, DepsCall, DepsPip
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import TransportableObject
from covalent.executor import _executor_manager
from covalent.executor.base import AsyncBaseExecutor, wrapper_fn

from .._db import upsert
from .._db.write_result_to_db import get_sublattice_electron_id
from . import data_manager as resultsvc
from . import dispatcher

app_log = logger.app_log
log_stack_info = logger.log_stack_info


# This is to be run out-of-process
def _build_sublattice_graph(sub: Lattice, *args, **kwargs):
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

    sub_dispatch_inputs = {"args": [serialized_callable], "kwargs": inputs["kwargs"]}
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

        sub_dispatch_id = resultsvc.make_dispatch(
            json_sublattice, parent_result_object, parent_electron_id
        )
        app_log.debug(f"Sublattice dispatch id: {sub_dispatch_id}")
        return sub_dispatch_id
    else:
        app_log.debug("Error building sublattice graph")
        stderr = res["stderr"]
        raise RuntimeError("Error building sublattice graph: {stderr}")


# Domain: runner
# to be called by _run_abstract_task
def _get_task_input_values(result_object: Result, abs_task_inputs: dict) -> dict:
    node_values = {}
    args = abs_task_inputs["args"]
    for node_id in args:
        value = result_object.lattice.transport_graph.get_node_value(node_id, "output")
        node_values[node_id] = value

    kwargs = abs_task_inputs["kwargs"]
    for key, node_id in kwargs.items():
        value = result_object.lattice.transport_graph.get_node_value(node_id, "output")
        node_values[node_id] = value

    return node_values


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

    abstract_inputs = dispatcher._get_abstract_task_inputs(node_id, node_name, result_object)
    input_values = _get_task_input_values(result_object, abstract_inputs)

    abstract_args = abstract_inputs["args"]
    abstract_kwargs = abstract_inputs["kwargs"]
    args = [input_values[node_id] for node_id in abstract_args]
    kwargs = {k: input_values[v] for k, v in abstract_kwargs.items()}
    task_input = {"args": args, "kwargs": kwargs}

    return task_input


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
    result_object = resultsvc.get_result_object(dispatch_id)

    try:
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
        start_time = datetime.now(timezone.utc)

        call_before, call_after = _gather_deps(result_object, node_id)

    except Exception as ex:
        app_log.error(f"Exception when trying to resolve inputs or deps: {ex}")
        node_result = resultsvc.generate_node_result(
            node_id=node_id, start_time=start_time, status=Result.FAILED, error=str(ex)
        )
        return node_result

    node_result = resultsvc.generate_node_result(
        node_id=node_id,
        start_time=start_time,
        status=Result.RUNNING,
    )
    app_log.debug(f"7: Marking node {node_id} as running (_run_abstract_task)")

    await resultsvc.update_node_result(result_object, node_result)

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
    except Exception as ex:
        app_log.debug(f"Exception when trying to instantiate executor: {ex}")
        node_result = resultsvc.generate_node_result(
            node_id=node_id,
            end_time=datetime.now(timezone.utc),
            status=Result.FAILED,
            error="".join(traceback.TracebackException.from_exception(ex).format()),
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

            node_result = resultsvc.generate_node_result(
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

            if isinstance(executor, AsyncBaseExecutor):
                output, stdout, stderr = await execute_callable()
            else:
                loop = asyncio.get_running_loop()
                output, stdout, stderr = await loop.run_in_executor(None, execute_callable)

            node_result = resultsvc.generate_node_result(
                node_id=node_id,
                end_time=datetime.now(timezone.utc),
                status=Result.COMPLETED,
                output=output,
                stdout=stdout,
                stderr=stderr,
            )

    except Exception as ex:
        app_log.error(f"Exception occurred when running task {node_id}: {ex}")
        node_result = resultsvc.generate_node_result(
            node_id=node_id,
            end_time=datetime.now(timezone.utc),
            status=Result.FAILED,
            error="".join(traceback.TracebackException.from_exception(ex).format()),
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
async def run_abstract_task_and_update(
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
    result_object = resultsvc.get_result_object(dispatch_id)
    await resultsvc.update_node_result(result_object, node_result)


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
    upsert._lattice_data(result_object)

    app_log.debug(f"Preparing to post-process workflow {result_object.dispatch_id}")

    if pp_executor == "client":
        app_log.debug("Workflow to be postprocessed client side")
        result_object._status = Result.PENDING_POSTPROCESSING
        result_object._end_time = datetime.now(timezone.utc)
        upsert._lattice_data(result_object)
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

        return result_object

    if post_process_result["status"] != Result.COMPLETED:
        err = post_process_result["stderr"]
        app_log.debug(f"Post-processing failed: {err}")
        result_object._status = Result.POSTPROCESSING_FAILED
        result_object._error = f"Post-processing failed: {err}"
        result_object._end_time = datetime.now(timezone.utc)
        upsert._lattice_data(result_object)

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


async def postprocess_workflow(dispatch_id: str) -> Result:
    result_object = resultsvc.get_result_object(dispatch_id)
    return await _postprocess_workflow(result_object)
