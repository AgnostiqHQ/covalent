# Copyright 2023 Agnostiq Inc.
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
Defines the core functionality of the new improved runner
"""

import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Dict

from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.exceptions import TaskCancelledError
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent.executor.base import AsyncBaseExecutor
from covalent.executor.schemas import ResourceMap, TaskSpec
from covalent.executor.utils import Signals

from . import data_manager as datamgr
from . import runner as runner_legacy
from .data_modules import asset_manager as am
from .runner_modules import executor_proxy, jobs
from .runner_modules.cancel import cancel_tasks  # nopycln: import
from .runner_modules.utils import get_executor

app_log = logger.app_log
log_stack_info = logger.log_stack_info
debug_mode = get_config("sdk.log_level") == "debug"

# Dedicated thread pool for invoking non-async Executor.cancel()
_cancel_threadpool = ThreadPoolExecutor()

# Asyncio Queue
_job_events = None

_job_event_listener = None

_futures = set()

# message format:
# Ready for retrieve result
# {"task_group_metadata": dict, "event": "READY"}
#
# Unable to retrieve result (e.g. credentials expired)
#
# {"task_group_metadata": dict, "event": "FAILED", "detail": str}


# Domain: runner
async def _submit_abstract_task_group(
    dispatch_id: str,
    task_group_id: int,
    task_seq: list,
    known_nodes: list,
    executor: AsyncBaseExecutor,
) -> None:
    # Task sequence of the form {"function_id": task_id, "args_ids":
    # [node_ids], "kwargs_ids": {key: node_id}}

    task_ids = [task["function_id"] for task in task_seq]
    task_specs = []
    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "task_group_id": task_group_id,
        "node_ids": task_ids,
    }

    try:
        if not type(executor).SUPPORTS_MANAGED_EXECUTION:
            raise NotImplementedError("Executor does not support managed execution")

        resources = {"functions": {}, "inputs": {}, "deps": {}}

        # Get upload URIs
        for task_spec in task_seq:
            task_id = task_spec["function_id"]

            function_uri = executor.get_upload_uri(task_group_metadata, f"function-{task_id}")
            deps_uri = executor.get_upload_uri(task_group_metadata, f"deps-{task_id}")
            call_before_uri = executor.get_upload_uri(
                task_group_metadata, f"call_before-{task_id}"
            )
            call_after_uri = executor.get_upload_uri(task_group_metadata, f"call_after-{task_id}")

            await am.upload_asset_for_nodes(dispatch_id, "function", {task_id: function_uri})
            await am.upload_asset_for_nodes(dispatch_id, "deps", {task_id: deps_uri})
            await am.upload_asset_for_nodes(dispatch_id, "call_before", {task_id: call_before_uri})
            await am.upload_asset_for_nodes(dispatch_id, "call_after", {task_id: call_after_uri})

            deps_id = f"deps-{task_id}"
            call_before_id = f"call_before-{task_id}"
            call_after_id = f"call_after-{task_id}"
            task_spec["deps_id"] = deps_id
            task_spec["call_before_id"] = call_before_id
            task_spec["call_after_id"] = call_after_id

            resources["functions"][task_id] = function_uri
            resources["deps"][deps_id] = deps_uri
            resources["deps"][call_before_id] = call_before_uri
            resources["deps"][call_after_id] = call_after_uri

            task_specs.append(TaskSpec(**task_spec))

        node_upload_uris = {
            node_id: executor.get_upload_uri(task_group_metadata, f"node_{node_id}")
            for node_id in known_nodes
        }
        resources["inputs"] = node_upload_uris

        app_log.debug(
            f"Uploading known nodes {known_nodes} for task group {dispatch_id}:{task_group_id}"
        )
        await am.upload_asset_for_nodes(dispatch_id, "output", node_upload_uris)

        ts = datetime.now(timezone.utc)
        node_results = [
            datamgr.generate_node_result(
                node_id=task_id,
                start_time=ts,
                status=RESULT_STATUS.RUNNING,
            )
            for task_id in task_ids
        ]

        # Use one proxy for the task group; handles the following requests:
        # - check if the job has a pending cancel request
        # - set the job handle
        # - set job status

        # Watch the task group
        fut = asyncio.create_task(executor_proxy.watch(dispatch_id, task_ids[0], executor))
        _futures.add(fut)
        fut.add_done_callback(_futures.discard)

        send_retval = await executor.send(
            task_specs,
            ResourceMap(**resources),
            task_group_metadata,
        )

        app_log.debug(f"Submitted task group {dispatch_id}:{task_group_id}")

    except TaskCancelledError:
        app_log.debug(f"Task group {dispatch_id}:{task_group_id} cancelled")

        send_retval = None

        node_results = [
            datamgr.generate_node_result(
                node_id=task_id,
                end_time=datetime.now(timezone.utc),
                status=RESULT_STATUS.CANCELLED,
            )
            for task_id in task_ids
        ]

    except Exception as ex:
        tb = "".join(traceback.TracebackException.from_exception(ex).format())
        app_log.debug(f"Exception occurred when running task group {task_group_id}:")
        app_log.debug(tb)
        error_msg = tb if debug_mode else str(ex)
        ts = datetime.now(timezone.utc)

        send_retval = None

        node_results = [
            datamgr.generate_node_result(
                node_id=task_id,
                end_time=datetime.now(timezone.utc),
                status=RESULT_STATUS.FAILED,
                error=error_msg,
            )
            for task_id in task_ids
        ]

    return node_results, send_retval


async def _get_task_result(task_group_metadata: Dict, data: Any):
    """Retrieve task results from executor.

    Parameters:
        task_group_metadata: metadata about the task group
        data: task execution information (such as status)

    Both `task_group_metadata` and `data` will be passed directly to
    Executor.receive().

    """

    dispatch_id = task_group_metadata["dispatch_id"]
    task_ids = task_group_metadata["node_ids"]
    gid = task_group_metadata["task_group_id"]
    app_log.debug(f"Pulling job artifacts for task group {dispatch_id}:{gid}")
    try:
        executor_attrs = await datamgr.electron.get(
            dispatch_id, gid, ["executor", "executor_data"]
        )
        executor_name = executor_attrs["executor"]
        executor_data = executor_attrs["executor_data"]

        executor = get_executor(
            node_id=gid,
            selected_executor=[executor_name, executor_data],
            loop=asyncio.get_running_loop(),
            pool=None,
        )

        # Expects a list of TaskUpdates
        task_group_results = await executor.receive(task_group_metadata, data)

        node_results = []
        for task_result in task_group_results:
            task_id = task_result.node_id
            status = task_result.status
            await am.download_assets_for_node(dispatch_id, task_id, task_result.assets)

            node_result = datamgr.generate_node_result(
                node_id=task_id,
                end_time=datetime.now(timezone.utc),
                status=status,
            )
            node_results.append(node_result)

    except Exception as ex:
        tb = "".join(traceback.TracebackException.from_exception(ex).format())
        app_log.debug(f"Exception occurred when receiving task group {gid}:")
        app_log.debug(tb)
        error_msg = tb if debug_mode else str(ex)
        ts = datetime.now(timezone.utc)

        node_results = [
            datamgr.generate_node_result(
                node_id=node_id,
                end_time=ts,
                status=RESULT_STATUS.FAILED,
                error=error_msg,
            )
            for node_id in task_ids
        ]

    for node_result in node_results:
        await datamgr.update_node_result(dispatch_id, node_result)


async def run_abstract_task_group(
    dispatch_id: str,
    task_group_id: int,
    task_seq: list,
    known_nodes: list,
    selected_executor: Any,
) -> None:
    executor = None

    try:
        app_log.debug(f"Attempting to instantiate executor {selected_executor}")
        task_ids = [task["function_id"] for task in task_seq]
        app_log.debug(f"Running task group {dispatch_id}:{task_group_id}")
        executor = get_executor(
            node_id=task_group_id,
            selected_executor=selected_executor,
            loop=asyncio.get_running_loop(),
            pool=None,
        )

        # Check if the job should be cancelled
        if await jobs.get_cancel_requested(dispatch_id, task_ids[0]):
            await jobs.put_job_status(dispatch_id, task_ids[0], RESULT_STATUS.CANCELLED)

            for task_id in task_ids:
                task_metadata = {"dispatch_id": dispatch_id, "node_id": task_id}
                app_log.debug(f"Refusing to execute cancelled task {dispatch_id}:{task_id}")
                await mark_task_ready(task_metadata, None)

            return

        # Legacy runner doesn't yet support task packing
        if not type(executor).SUPPORTS_MANAGED_EXECUTION:
            if len(task_seq) != 1:
                raise RuntimeError("Task packing not supported by executor plugin")

            task_spec = task_seq[0]
            node_id = task_spec["function_id"]
            name = task_spec["name"]
            abstract_inputs = {
                "args": task_spec["args_ids"],
                "kwargs": task_spec["kwargs_ids"],
            }
            app_log.debug(f"Reverting to legacy runner for task {task_group_id}")
            coro = runner_legacy.run_abstract_task(
                dispatch_id,
                node_id,
                name,
                abstract_inputs,
                selected_executor,
            )
            fut = asyncio.create_task(coro)
            _futures.add(fut)
            fut.add_done_callback(_futures.discard)
            return

        node_results, send_retval = await _submit_abstract_task_group(
            dispatch_id,
            task_group_id,
            task_seq,
            known_nodes,
            executor,
        )

    except Exception as ex:
        tb = "".join(traceback.TracebackException.from_exception(ex).format())
        app_log.debug("Exception when trying to instantiate executor:")
        app_log.debug(tb)
        error_msg = tb if debug_mode else str(ex)
        ts = datetime.now(timezone.utc)

        send_retval = None
        node_results = [
            datamgr.generate_node_result(
                node_id=node_id,
                start_time=ts,
                end_time=ts,
                status=RESULT_STATUS.FAILED,
                error=error_msg,
            )
            for node_id in task_ids
        ]

    for node_result in node_results:
        await datamgr.update_node_result(dispatch_id, node_result)

    if node_results[0]["status"] == RESULT_STATUS.RUNNING:
        task_group_metadata = {
            "dispatch_id": dispatch_id,
            "node_ids": task_ids,
            "task_group_id": task_group_id,
        }
        await _poll_task_status(task_group_metadata, executor, send_retval)

    # Terminate proxy
    if executor:
        executor._notify(Signals.EXIT)
        app_log.debug(f"Stopping proxy for task group {dispatch_id}:{task_group_id}")


async def _listen_for_job_events():
    app_log.debug("Starting event listener")
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
                task_group_metadata = msg["task_group_metadata"]
                detail = msg["detail"]
                fut = asyncio.create_task(_get_task_result(task_group_metadata, detail))
                _futures.add(fut)
                fut.add_done_callback(_futures.discard)
                continue

            if event == "FAILED":
                task_group_metadata = msg["task_group_metadata"]
                dispatch_id = task_group_metadata["dispatch_id"]
                gid = task_group_metadata["task_group_id"]
                task_ids = task_group_metadata["node_ids"]
                detail = msg["detail"]
                ts = datetime.now(timezone.utc)
                for task_id in task_ids:
                    node_result = datamgr.generate_node_result(
                        node_id=task_id,
                        end_time=ts,
                        status=RESULT_STATUS.FAILED,
                        error=detail,
                    )
                    await datamgr.update_node_result(dispatch_id, node_result)

        except Exception as ex:
            app_log.exception("Error reading message: {ex}")


async def _mark_ready(task_group_metadata: dict, detail: Any):
    await _job_events.put(
        {"task_group_metadata": task_group_metadata, "event": "READY", "detail": detail}
    )


async def _mark_failed(task_group_metadata: dict, detail: str):
    await _job_events.put(
        {"task_group_metadata": task_group_metadata, "event": "FAILED", "detail": detail}
    )


async def _poll_task_status(
    task_group_metadata: Dict, executor: AsyncBaseExecutor, poll_data: Any
):
    """Polls a group of tasks until it terminates.

    `poll_data` is the return value of `Executor.send()` and will be
    passed directly to `Executor.poll()`.

    """
    # Return immediately if no polling logic (default return value is -1)

    dispatch_id = task_group_metadata["dispatch_id"]
    task_group_id = task_group_metadata["task_group_id"]
    task_ids = task_group_metadata["node_ids"]

    try:
        app_log.debug(f"Polling status for task group {dispatch_id}:{task_group_id}")
        receive_data = await executor.poll(task_group_metadata, poll_data)
        await _mark_ready(task_group_metadata, receive_data)

    except NotImplementedError:
        app_log.debug(f"Executor {executor.short_name()} is async.")

    except TaskCancelledError:
        app_log.debug(f"Task group {dispatch_id}:{task_group_id} cancelled")
        await _mark_ready(task_group_metadata, None)

    except Exception as ex:
        task_group_id = task_group_metadata["task_group_id"]
        tb = "".join(traceback.TracebackException.from_exception(ex).format())
        app_log.debug(f"Exception occurred when polling task {task_group_id}:")
        app_log.debug(tb)
        error_msg = tb if debug_mode else str(ex)
        await _mark_failed(task_group_metadata, error_msg)


async def mark_task_ready(task_metadata: dict, detail: Any):
    dispatch_id = task_metadata["dispatch_id"]
    node_id = task_metadata["node_id"]
    gid = (await datamgr.electron.get(dispatch_id, node_id, ["task_group_id"]))["task_group_id"]
    task_group_metadata = {
        "dispatch_id": dispatch_id,
        "node_ids": [node_id],
        "task_group_id": gid,
    }

    await _mark_ready(task_group_metadata, detail)
