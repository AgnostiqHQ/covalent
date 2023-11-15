# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Defines the core functionality of the legacy runner
"""

import asyncio
import traceback
from datetime import datetime, timezone
from functools import partial
from typing import Any, Dict, List, Tuple

from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._workflow import DepsBash, DepsCall, DepsPip
from covalent.executor.utils.wrappers import wrapper_fn

from . import data_manager as datasvc
from .runner_modules import executor_proxy
from .runner_modules.utils import get_executor

app_log = logger.app_log
log_stack_info = logger.log_stack_info
debug_mode = get_config("sdk.log_level") == "debug"


# Domain: runner
# to be called by _run_abstract_task
async def _get_task_input_values(dispatch_id: str, abs_task_inputs: dict) -> dict:
    node_values = {}
    args = abs_task_inputs["args"]
    for node_id in args:
        value = (await datasvc.electron.get(dispatch_id, node_id, ["output"]))["output"]
        node_values[node_id] = value

    kwargs = abs_task_inputs["kwargs"]
    for key, node_id in kwargs.items():
        value = (await datasvc.electron.get(dispatch_id, node_id, ["output"]))["output"]
        node_values[node_id] = value

    return node_values


# Domain: runner
async def _run_abstract_task(
    dispatch_id: str,
    node_id: int,
    node_name: str,
    abstract_inputs: Dict,
    selected_executor: Any,
) -> None:
    # Resolve abstract task and inputs to their concrete (serialized) values
    timestamp = datetime.now(timezone.utc)

    try:
        serialized_callable = (await datasvc.electron.get(dispatch_id, node_id, ["function"]))[
            "function"
        ]

        input_values = await _get_task_input_values(dispatch_id, abstract_inputs)

        abstract_args = abstract_inputs["args"]
        abstract_kwargs = abstract_inputs["kwargs"]
        args = [input_values[node_id] for node_id in abstract_args]
        kwargs = {k: input_values[v] for k, v in abstract_kwargs.items()}

        task_input = {"args": args, "kwargs": kwargs}

        app_log.debug(f"Collecting deps for task {node_id}")

        call_before, call_after = await _gather_deps(dispatch_id, node_id)

    except Exception as ex:
        app_log.error(f"Exception when trying to resolve inputs or deps: {ex}")
        node_result = datasvc.generate_node_result(
            node_id=node_id,
            start_time=timestamp,
            end_time=timestamp,
            status=RESULT_STATUS.FAILED,
            error=str(ex),
        )
        return node_result

    node_result = datasvc.generate_node_result(
        node_name=node_name,
        node_id=node_id,
        start_time=timestamp,
        status=RESULT_STATUS.RUNNING,
    )
    app_log.debug(f"7: Marking node {node_id} as running (_run_abstract_task)")

    await datasvc.update_node_result(dispatch_id, node_result)

    return await _run_task(
        dispatch_id=dispatch_id,
        node_id=node_id,
        serialized_callable=serialized_callable,
        selected_executor=selected_executor,
        node_name=node_name,
        call_before=call_before,
        call_after=call_after,
        inputs=task_input,
    )


# Domain: runner
async def _run_task(
    dispatch_id: str,
    node_id: int,
    inputs: Dict,
    serialized_callable: Any,
    selected_executor: Any,
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
        node_id: Node id of the task to be executed.

    Returns:
        None
    """

    dispatch_info = await datasvc.dispatch.get(dispatch_id, ["results_dir"])
    results_dir = dispatch_info["results_dir"]

    # Instantiate the executor from JSON
    try:
        app_log.debug(f"Instantiating executor for {dispatch_id}:{node_id}")
        executor = get_executor(
            node_id=node_id,
            selected_executor=selected_executor,
            loop=asyncio.get_running_loop(),
            pool=None,
        )
    except Exception as ex:
        tb = "".join(traceback.TracebackException.from_exception(ex).format())
        app_log.debug("Exception when trying to instantiate executor:")
        app_log.debug(tb)
        error_msg = tb if debug_mode else str(ex)
        node_result = datasvc.generate_node_result(
            node_id=node_id,
            end_time=datetime.now(timezone.utc),
            status=RESULT_STATUS.FAILED,
            error=error_msg,
        )
        return node_result

    # run the task on the executor and register any failures
    try:
        app_log.debug(f"Executing task {node_name}")

        assembled_callable = partial(wrapper_fn, serialized_callable, call_before, call_after)

        # Start listening for messages from the plugin
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
            node_id=node_id,
            node_name=node_name,
            end_time=datetime.now(timezone.utc),
            status=RESULT_STATUS.FAILED,
            error=error_msg,
        )
    app_log.debug(f"Node result: {node_result}")
    return node_result


# Domain: runner
async def _gather_deps(dispatch_id: str, node_id: int) -> Tuple[List, List]:
    """Assemble deps for a node into the final call_before and call_after"""

    deps_attrs = await datasvc.electron.get(
        dispatch_id, node_id, ["deps", "call_before", "call_after"]
    )

    deps = deps_attrs["deps"]

    # Assemble call_before and call_after from all the deps

    call_before_objs_json = deps_attrs["call_before"]
    call_after_objs_json = deps_attrs["call_after"]

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
) -> None:
    node_result = await _run_abstract_task(
        dispatch_id=dispatch_id,
        node_id=node_id,
        node_name=node_name,
        abstract_inputs=abstract_inputs,
        selected_executor=selected_executor,
    )
    await datasvc.update_node_result(dispatch_id, node_result)
