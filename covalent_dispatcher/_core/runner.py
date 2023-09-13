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
import importlib
import json
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from functools import partial
from typing import Any, Dict, List, Literal, Tuple, Union

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._workflow import DepsBash, DepsCall, DepsPip
from covalent._workflow.transport import TransportableObject
from covalent.executor import _executor_manager
from covalent.executor.base import AsyncBaseExecutor, wrapper_fn
from covalent.executor.utils import set_context

from . import data_manager as datasvc
from .data_modules.job_manager import get_jobs_metadata, set_cancel_result
from .runner_modules import executor_proxy

app_log = logger.app_log
log_stack_info = logger.log_stack_info
debug_mode = get_config("sdk.log_level") == "debug"

_cancel_threadpool = ThreadPoolExecutor()


# Domain: runner
def get_executor(
    executor: Union[Tuple, List],
    loop: asyncio.BaseEventLoop = None,
    cancel_pool: ThreadPoolExecutor = None,
) -> AsyncBaseExecutor:
    """Get unpacked and initialized executor object.

    Args:
        executor: Tuple containing short name and object dictionary for the executor.
        loop: Running event loop. Defaults to None.
        cancel_pool: Threadpool for cancelling tasks. Defaults to None.

    Returns:
        Executor object.

    """
    short_name, object_dict = executor
    executor = _executor_manager.get_executor(short_name)
    executor.from_dict(object_dict)
    executor._init_runtime(loop=loop, cancel_pool=cancel_pool)

    return executor


# Domain: runner
# to be called by _run_abstract_task
def _get_task_input_values(result_object: Result, abs_task_inputs: dict) -> dict:
    """
    Retrieve the input values from the result_object for the task

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
async def run_abstract_task(
    dispatch_id: str,
    node_id: int,
    node_name: str,
    abstract_inputs: Dict,
    executor: Any,
) -> None:
    node_result = await _run_abstract_task(
        dispatch_id=dispatch_id,
        node_id=node_id,
        node_name=node_name,
        abstract_inputs=abstract_inputs,
        executor=executor,
    )

    result_object = datasvc.get_result_object(dispatch_id)
    await datasvc.update_node_result(result_object, node_result)


# Domain: runner
async def _run_abstract_task(
    dispatch_id: str,
    node_id: int,
    node_name: str,
    abstract_inputs: Dict,
    executor: Any,
) -> None:
    # Resolve abstract task and inputs to their concrete (serialized) values
    result_object = datasvc.get_result_object(dispatch_id)
    timestamp = datetime.now(timezone.utc)

    try:
        cancel_req = await executor_proxy._get_cancel_requested(dispatch_id, node_id)
        if cancel_req:
            app_log.debug(f"Don't run cancelled task {dispatch_id}:{node_id}")
            return datasvc.generate_node_result(
                dispatch_id=dispatch_id,
                node_id=node_id,
                node_name=node_name,
                start_time=timestamp,
                end_time=timestamp,
                status=RESULT_STATUS.CANCELLED,
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
            dispatch_id=dispatch_id,
            node_id=node_id,
            node_name=node_name,
            start_time=timestamp,
            end_time=timestamp,
            status=RESULT_STATUS.FAILED,
            error=str(ex),
        )
        return node_result

    node_result = datasvc.generate_node_result(
        dispatch_id=dispatch_id,
        node_id=node_id,
        node_name=node_name,
        start_time=timestamp,
        status=RESULT_STATUS.RUNNING,
    )
    app_log.debug(f"7: Marking node {node_id} as running (_run_abstract_task)")

    await datasvc.update_node_result(result_object, node_result)

    return await _run_task(
        result_object=result_object,
        node_id=node_id,
        serialized_callable=serialized_callable,
        executor=executor,
        node_name=node_name,
        call_before=call_before,
        call_after=call_after,
        inputs=task_input,
    )


# Domain: runner
async def _run_task(
    result_object: Result,
    node_id: int,
    inputs: Dict,
    serialized_callable: Any,
    executor: Any,
    call_before: List,
    call_after: List,
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
    dispatch_id = result_object.dispatch_id
    results_dir = result_object.results_dir

    # Instantiate the executor from JSON
    try:
        executor = get_executor(executor=executor, loop=asyncio.get_running_loop())

    except Exception as ex:
        tb = "".join(traceback.TracebackException.from_exception(ex).format())
        app_log.debug("Exception when trying to instantiate executor:")
        app_log.debug(tb)
        error_msg = tb if debug_mode else str(ex)
        node_result = datasvc.generate_node_result(
            dispatch_id=dispatch_id,
            node_id=node_id,
            node_name=node_name,
            end_time=datetime.now(timezone.utc),
            status=RESULT_STATUS.FAILED,
            error=error_msg,
        )
        return node_result

    # Run the task on the executor and register any failures.
    try:
        app_log.debug(f"Executing task {node_name}")

        def qelectron_compatible_wrapper(node_id, dispatch_id, ser_user_fn, *args, **kwargs):
            user_fn = ser_user_fn.get_deserialized()

            try:
                mod_qe_utils = importlib.import_module("covalent._shared_files.qelectron_utils")

                with set_context(node_id, dispatch_id):
                    res = user_fn(*args, **kwargs)
                    mod_qe_utils.print_qelectron_db()

                return res
            except ModuleNotFoundError:
                return user_fn(*args, **kwargs)

        serialized_callable = TransportableObject(
            partial(qelectron_compatible_wrapper, node_id, dispatch_id, serialized_callable)
        )

        assembled_callable = partial(wrapper_fn, serialized_callable, call_before, call_after)

        # Note: Executor proxy monitors the executors instances and watches the send and receive queues of the executor.
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
            dispatch_id=dispatch_id,
            node_id=node_id,
            node_name=node_name,
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
            dispatch_id=dispatch_id,
            node_id=node_id,
            node_name=node_name,
            end_time=datetime.now(timezone.utc),
            status=RESULT_STATUS.FAILED,
            error=error_msg,
        )
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
        executor = get_executor(
            executor=executor, loop=asyncio.get_running_loop(), cancel_pool=_cancel_threadpool
        )
        task_metadata = {"dispatch_id": dispatch_id, "node_id": task_id}
        cancel_job_result = await executor._cancel(task_metadata, json.loads(job_handle))

    except Exception as ex:
        app_log.debug(f"Exception when cancel task {dispatch_id}:{task_id}: {ex}")
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
        node_ids: List of node ids from the workflow to retrieve the metadata for

    Return(s)
        List of node metadata for the given `node_ids`
    """
    res = datasvc.get_result_object(dispatch_id)
    tg = res.lattice.transport_graph
    return list(map(lambda x: tg.get_node_value(x, "metadata"), node_ids))
