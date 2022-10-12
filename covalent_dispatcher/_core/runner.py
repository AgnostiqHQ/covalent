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
import traceback
from datetime import datetime, timezone
from functools import partial
from typing import Any, Dict, List, Tuple

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.defaults import sublattice_prefix
from covalent._workflow import DepsBash, DepsCall, DepsPip
from covalent.executor import _executor_manager
from covalent.executor.base import AsyncBaseExecutor, wrapper_fn

from .._db import upsert
from .._db.write_result_to_db import get_sublattice_electron_id
from . import dispatcher
from . import result as resultsvc

app_log = logger.app_log
log_stack_info = logger.log_stack_info


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
    result_object: Result,
    node_id: int,
    node_name: str,
    abstract_inputs: Dict,
    selected_executor: Any,
    workflow_executor: Any,
) -> None:

    # Resolve abstract task and inputs to their concrete (serialized) values
    serialized_callable = result_object.lattice.transport_graph.get_node_value(node_id, "function")
    input_values = _get_task_input_values(result_object, abstract_inputs)

    abstract_args = abstract_inputs["args"]
    abstract_kwargs = abstract_inputs["kwargs"]
    args = [input_values[node_id] for node_id in abstract_args]
    kwargs = {k: input_values[v] for k, v in abstract_kwargs.items()}
    task_input = {"args": args, "kwargs": kwargs}

    try:
        call_before, call_after = _gather_deps(result_object, node_id)

    except Exception as ex:
        app_log.error(f"Exception when trying to collect deps: {ex}")
        raise ex

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

            # Read the result object directly from the server

            sublattice_result = await dispatcher._dispatch_sync_sublattice(
                parent_result_object=result_object,
                parent_electron_id=sub_electron_id,
                inputs=inputs,
                serialized_callable=serialized_callable,
                workflow_executor=workflow_executor,
            )

            if not sublattice_result:
                raise RuntimeError("Sublattice execution failed")

            output = sublattice_result.encoded_result
            end_time = datetime.now(timezone.utc)
            node_result = resultsvc.generate_node_result(
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

                upsert._lattice_data(sublattice_result)

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
async def _run_task_and_update(run_task_callable, result_object, pending_deps, status_queue):
    node_result = await run_task_callable()

    # NOTE: This is a blocking operation because of db writes and needs special handling when
    # we switch to an event loop for processing tasks
    await resultsvc._update_node_result(result_object, node_result, pending_deps, status_queue)
    return node_result
