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
Module for defining a local executor that directly invokes the input python function.

This is a plugin executor module; it is loaded if found and properly structured.
"""

import asyncio
import os
from concurrent.futures import ProcessPoolExecutor
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import requests
from pydantic import BaseModel

from covalent._shared_files import TaskCancelledError, TaskRuntimeError, logger
from covalent._shared_files.config import get_config
from covalent._shared_files.util_classes import RESULT_STATUS, Status
from covalent._shared_files.utils import format_server_url
from covalent.executor import BaseExecutor

# Relative imports are not allowed in executor plugins
from covalent.executor.schemas import ResourceMap, TaskSpec, TaskUpdate

# Store the wrapper function in an external module to avoid module
# import errors during pickling
from covalent.executor.utils.wrappers import io_wrapper, run_task_from_uris

# The plugin class name must be given by the executor_plugin_name attribute:
EXECUTOR_PLUGIN_NAME = "LocalExecutor"

app_log = logger.app_log
log_stack_info = logger.log_stack_info

_EXECUTOR_PLUGIN_DEFAULTS = {
    "log_stdout": "stdout.log",
    "log_stderr": "stderr.log",
    "cache_dir": os.path.join(
        os.environ.get("XDG_CACHE_HOME") or os.path.join(os.environ["HOME"], ".cache"), "covalent"
    ),
    "workdir": os.path.join(
        os.environ.get("XDG_CACHE_HOME") or os.path.join(os.environ["HOME"], ".cache"),
        "covalent",
        "workdir",
    ),
    "create_unique_workdir": False,
}


proc_pool = ProcessPoolExecutor()


# Valid terminal statuses
class StatusEnum(str, Enum):
    CANCELLED = str(RESULT_STATUS.CANCELLED)
    COMPLETED = str(RESULT_STATUS.COMPLETED)
    FAILED = str(RESULT_STATUS.FAILED)


class ReceiveModel(BaseModel):
    status: StatusEnum


MANAGED_EXECUTION = True


class LocalExecutor(BaseExecutor):
    """
    Local executor class that directly invokes the input function.
    """

    SUPPORTS_MANAGED_EXECUTION = MANAGED_EXECUTION

    def __init__(
        self, workdir: str = "", create_unique_workdir: Optional[bool] = None, *args, **kwargs
    ) -> None:
        if not workdir:
            try:
                workdir = get_config("executors.local.workdir")
            except KeyError:
                workdir = _EXECUTOR_PLUGIN_DEFAULTS["workdir"]
                debug_msg = f"Couldn't find `executors.local.workdir` in config, using default value {workdir}."
                app_log.debug(debug_msg)

        if create_unique_workdir is None:
            try:
                create_unique_workdir = get_config("executors.local.create_unique_workdir")
            except KeyError:
                create_unique_workdir = _EXECUTOR_PLUGIN_DEFAULTS["create_unique_workdir"]
                debug_msg = f"Couldn't find `executors.local.create_unique_workdir` in config, using default value {create_unique_workdir}."
                app_log.debug(debug_msg)

        super().__init__(*args, **kwargs)

        self.workdir = workdir
        self.create_unique_workdir = create_unique_workdir

    def run(self, function: Callable, args: List, kwargs: Dict, task_metadata: Dict) -> Any:
        """
        Execute the function locally

        Arg(s)
            function: Function to be executed
            args: Arguments passed to the function
            kwargs: Keyword arguments passed to the function
            task_metadata: Metadata of the task to be executed

        Return(s)
            Task output
        """

        app_log.debug(f"Running function {function} locally")

        self.set_job_handle(42)

        if self.get_cancel_requested():
            app_log.debug("Task has been cancelled don't proceed")
            raise TaskCancelledError

        dispatch_id = task_metadata["dispatch_id"]
        node_id = task_metadata["node_id"]

        if self.create_unique_workdir:
            current_workdir = os.path.join(self.workdir, dispatch_id, f"node_{node_id}")
        else:
            current_workdir = self.workdir

        # Run the target function in a separate process
        fut = proc_pool.submit(io_wrapper, function, args, kwargs, current_workdir)

        output, worker_stdout, worker_stderr, tb = fut.result()

        print(worker_stdout, end="", file=self.task_stdout)
        print(worker_stderr, end="", file=self.task_stderr)

        if tb:
            print(tb, end="", file=self.task_stderr)
            raise TaskRuntimeError(tb)

        return output

    def _send(
        self,
        task_specs: List[TaskSpec],
        resources: ResourceMap,
        task_group_metadata: dict,
    ):
        dispatch_id = task_group_metadata["dispatch_id"]
        task_ids = task_group_metadata["node_ids"]
        gid = task_group_metadata["task_group_id"]
        output_uris = []
        for node_id in task_ids:
            result_uri = os.path.join(self.cache_dir, f"result_{dispatch_id}-{node_id}.pkl")
            stdout_uri = os.path.join(self.cache_dir, f"stdout_{dispatch_id}-{node_id}.txt")
            stderr_uri = os.path.join(self.cache_dir, f"stderr_{dispatch_id}-{node_id}.txt")
            qelectron_db_uri = os.path.join(
                self.cache_dir, f"qelectron_db_{dispatch_id}-{node_id}.mdb"
            )
            output_uris.append((result_uri, stdout_uri, stderr_uri, qelectron_db_uri))

        server_url = format_server_url()

        app_log.debug(f"Running task group {dispatch_id}:{task_ids}")
        future = proc_pool.submit(
            run_task_from_uris,
            list(map(lambda t: t.model_dump(), task_specs)),
            resources.model_dump(),
            output_uris,
            self.cache_dir,
            task_group_metadata,
            server_url,
        )

        def handle_cancelled(fut):
            app_log.debug(f"In done callback for {dispatch_id}:{gid}, future {fut}")
            if fut.cancelled():
                for task_id in task_ids:
                    url = f"{server_url}/api/v2/dispatches/{dispatch_id}/electrons/{task_id}/job"
                    requests.put(url, json={"status": "CANCELLED"})

        future.add_done_callback(handle_cancelled)

    def _receive(self, task_group_metadata: Dict, data: Any) -> List[TaskUpdate]:
        # Returns (output_uri, stdout_uri, stderr_uri,
        # exception_raised)

        # Job should have reached a terminal state by the time this is invoked.
        dispatch_id = task_group_metadata["dispatch_id"]
        task_ids = task_group_metadata["node_ids"]

        task_results = []

        for task_id in task_ids:
            # Handle the case where the job was cancelled before the task started running
            app_log.debug(f"Receive called for task {dispatch_id}:{task_id} with data {data}")

            if not data:
                terminal_status = RESULT_STATUS.CANCELLED
            else:
                received = ReceiveModel.model_validate(data)
                terminal_status = Status(received.status.value)

            task_result = {
                "dispatch_id": dispatch_id,
                "node_id": task_id,
                "status": terminal_status,
                "assets": {
                    "output": {
                        "remote_uri": "",
                    },
                    "stdout": {
                        "remote_uri": "",
                    },
                    "stderr": {
                        "remote_uri": "",
                    },
                    "qelectron_db": {
                        "remote_uri": "",
                    },
                },
            }

            task_results.append(TaskUpdate(**task_result))

        app_log.debug(f"Returning results for tasks {dispatch_id}:{task_ids}")
        return task_results

    async def send(
        self,
        task_specs: List[TaskSpec],
        resources: ResourceMap,
        task_group_metadata: dict,
    ):
        # Assets are assumed to be accessible by the compute backend
        # at the provided URIs

        # The Asset Manager is responsible for uploading all assets
        # Returns a job handle (should be JSONable)

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self._send,
            task_specs,
            resources,
            task_group_metadata,
        )

    async def receive(self, task_group_metadata: Dict, data: Any) -> List[TaskUpdate]:
        # Returns (output_uri, stdout_uri, stderr_uri,
        # exception_raised)

        # Job should have reached a terminal state by the time this is invoked.
        loop = asyncio.get_running_loop()

        return await loop.run_in_executor(
            None,
            self._receive,
            task_group_metadata,
            data,
        )
