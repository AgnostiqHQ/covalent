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
from typing import Any, Dict

from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.defaults import sublattice_prefix
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._shared_files.utils import _log_mem
from covalent.executor.base import AsyncBaseExecutor

from . import data_manager as datamgr
from . import runner as runner_legacy
from .data_modules import asset_manager as am
from .runner_modules.utils import get_executor

app_log = logger.app_log
log_stack_info = logger.log_stack_info
debug_mode = get_config("sdk.log_level") == "debug"

# Asyncio Queue
_job_events = None

# This should go in the Jobs table
_job_handles = {}

_job_event_listener = None

# message format:
# Ready for retrieve result
# {"task_metadata": dict, "event": "READY"}
#
# Unable to retrieve result (e.g. credentials expired)
#
# {"task_metadata": dict, "event": "FAILED", "detail": str}


# Domain: runner
async def _submit_abstract_task(
    dispatch_id: str,
    task_id: int,
    node_name: str,
    abstract_inputs: Dict,
    executor: AsyncBaseExecutor,
) -> None:

    try:

        if not type(executor).SUPPORTS_MANAGED_EXECUTION:
            raise NotImplementedError("Executor does not support managed execution")

        if node_name.startswith(sublattice_prefix):
            raise NotImplementedError("Sublattices not yet supported")

        # Get upload URIs

        node_result = datamgr.generate_node_result(
            node_id=task_id,
            start_time=datetime.now(timezone.utc),
            status=RESULT_STATUS.RUNNING,
        )

        task_metadata = {"dispatch_id": dispatch_id, "node_id": task_id}

        function_uri = executor.get_upload_uri(task_metadata, "function")
        deps_uri = executor.get_upload_uri(task_metadata, "deps")
        call_before_uri = executor.get_upload_uri(task_metadata, "call_before")
        call_after_uri = executor.get_upload_uri(task_metadata, "call_after")

        abstract_args = abstract_inputs["args"]
        abstract_kwargs = abstract_inputs["kwargs"]

        distinct_nodes = set(abstract_args + list(abstract_kwargs.values()))

        node_upload_uris = {
            node_id: executor.get_upload_uri(task_metadata, f"node_{node_id}")
            for node_id in distinct_nodes
        }

        await am.upload_asset_for_nodes(dispatch_id, "function", {task_id: function_uri})
        await am.upload_asset_for_nodes(dispatch_id, "deps", {task_id: deps_uri})
        await am.upload_asset_for_nodes(dispatch_id, "call_before", {task_id: call_before_uri})
        await am.upload_asset_for_nodes(dispatch_id, "call_after", {task_id: call_after_uri})

        await am.upload_asset_for_nodes(dispatch_id, "output", node_upload_uris)

        args_uris = [node_upload_uris[node_id] for node_id in abstract_args]
        kwargs_uris = {k: node_upload_uris[v] for k, v in abstract_kwargs.items()}

        _log_mem(dispatch_id, task_id, RESULT_STATUS.RUNNING, "Runner(new): before send")
        job_handle = await executor.send(
            function_uri,
            deps_uri,
            call_before_uri,
            call_after_uri,
            args_uris,
            kwargs_uris,
            task_metadata,
        )
        _log_mem(dispatch_id, task_id, RESULT_STATUS.RUNNING, "Runner(new): after send")
        _job_handles[(dispatch_id, task_id)] = job_handle

    except Exception as ex:
        tb = "".join(traceback.TracebackException.from_exception(ex).format())
        app_log.debug(f"Exception occurred when running task {task_id}:")
        app_log.debug(tb)
        error_msg = tb if debug_mode else str(ex)
        node_result = datamgr.generate_node_result(
            node_id=task_id,
            end_time=datetime.now(timezone.utc),
            status=RESULT_STATUS.FAILED,
            error=error_msg,
        )

    return node_result


async def _get_task_result(task_metadata: Dict):
    try:
        dispatch_id = task_metadata["dispatch_id"]
        task_id = task_metadata["node_id"]
        app_log.debug(f"Pulling job artifacts for task {dispatch_id}:{task_id}")

        executor_name = await datamgr.get_electron_attribute(dispatch_id, task_id, "executor")
        executor_data = await datamgr.get_electron_attribute(dispatch_id, task_id, "executor_data")

        executor = get_executor(task_id, [executor_name, executor_data])

        job_handle = _job_handles.pop((dispatch_id, task_id))
        _log_mem(dispatch_id, task_id, RESULT_STATUS.RUNNING, "Runner(new): before receive")
        output_uri, stdout_uri, stderr_uri, status = await executor.receive(
            task_metadata, job_handle
        )

        src_uris = {"output": output_uri, "stdout": stdout_uri, "stderr": stderr_uri}
        node_result = datamgr.generate_node_result(
            node_id=task_id, end_time=datetime.now(timezone.utc), status=status
        )
        node_result["output_uri"] = output_uri
        node_result["stdout_uri"] = stdout_uri
        node_result["stderr_uri"] = stderr_uri
        _log_mem(dispatch_id, task_id, RESULT_STATUS.RUNNING, "Runner(new): after receive")

    except Exception as ex:
        tb = "".join(traceback.TracebackException.from_exception(ex).format())
        app_log.debug(f"Exception occurred when running task {task_id}:")
        app_log.debug(tb)
        error_msg = tb if debug_mode else str(ex)
        node_result = datamgr.generate_node_result(
            node_id=task_id,
            end_time=datetime.now(timezone.utc),
            status=RESULT_STATUS.FAILED,
            error=error_msg,
        )

    await datamgr.update_node_result(dispatch_id, node_result)


async def run_abstract_task(
    dispatch_id: str,
    node_id: int,
    node_name: str,
    abstract_inputs: Dict,
    selected_executor: Any,
    workflow_executor: Any,
) -> None:

    global _job_events
    if not _job_events:
        _job_events = asyncio.Queue()

    global _job_event_listener
    if not _job_event_listener:
        _job_event_listener = asyncio.create_task(_listen_for_job_events())

    try:
        app_log.debug(f"Attempting to instantiate executor {selected_executor}")
        executor = get_executor(node_id, selected_executor)
        if not type(executor).SUPPORTS_MANAGED_EXECUTION or node_name.startswith(
            sublattice_prefix
        ):
            coro = runner_legacy.run_abstract_task(
                dispatch_id,
                node_id,
                node_name,
                abstract_inputs,
                selected_executor,
                workflow_executor,
            )
            app_log.debug(f"Using legacy runner for task {dispatch_id}:{node_id}")
            asyncio.create_task(coro)
            return

        node_result = await _submit_abstract_task(
            dispatch_id,
            node_id,
            node_name,
            abstract_inputs,
            executor,
        )

    except Exception as ex:
        tb = "".join(traceback.TracebackException.from_exception(ex).format())
        app_log.debug("Exception when trying to instantiate executor:")
        app_log.debug(tb)
        error_msg = tb if debug_mode else str(ex)
        ts = datetime.now(timezone.utc)
        node_result = datamgr.generate_node_result(
            node_id=node_id,
            start_time=ts,
            end_time=ts,
            status=RESULT_STATUS.FAILED,
            error=error_msg,
        )

    await datamgr.update_node_result(dispatch_id, node_result)
    if node_result["status"] == RESULT_STATUS.RUNNING:
        task_metadata = {"dispatch_id": dispatch_id, "node_id": node_id}
        await _poll_task_status(task_metadata, executor)


async def _listen_for_job_events():
    while True:
        msg = await _job_events.get()
        try:
            event = msg["event"]
            app_log.debug(f"Received job event {event}")
            if event == "BYE":
                app_log.debug("Terminating job event listener")
                break

            # job has reached a terminal state
            if event == "READY":
                task_metadata = msg["task_metadata"]
                asyncio.create_task(_get_task_result(task_metadata))
                continue

            if event == "FAILED":
                task_metadata = msg["task_metadata"]
                dispatch_id = task_metadata["dispatch_id"]
                node_id = task_metadata["node_id"]
                detail = msg["detail"]
                node_result = datamgr.generate_node_result(
                    node_id=node_id,
                    end_time=datetime.now(timezone.utc),
                    status=RESULT_STATUS.FAILED,
                    error=detail,
                )
                await datamgr.update_node_result(dispatch_id, node_result)

        except Exception as ex:
            app_log.exception("Error reading message: {ex}")


async def _mark_ready(task_metadata: dict):
    await _job_events.put({"task_metadata": task_metadata, "event": "READY"})


async def _mark_failed(task_metadata: dict, detail: str):
    await _job_events.put({"task_metadata": task_metadata, "event": "FAILED", "detail": detail})


async def _poll_task_status(task_metadata: Dict, executor: AsyncBaseExecutor):
    # Return immediately if no polling logic (default return value is -1)

    dispatch_id = task_metadata["dispatch_id"]
    task_id = task_metadata["node_id"]

    try:
        job_handle = _job_handles[(dispatch_id, task_id)]

        app_log.debug(f"Polling task status for {dispatch_id}:{task_id}")
        if await executor.poll(task_metadata, job_handle) == 0:
            await _mark_ready(task_metadata)
    except Exception as ex:

        task_id = task_metadata["node_id"]
        tb = "".join(traceback.TracebackException.from_exception(ex).format())
        app_log.debug(f"Exception occurred when polling task {task_id}:")
        app_log.debug(tb)
        error_msg = tb if debug_mode else str(ex)
        await _mark_failed(task_metadata, error_msg)
