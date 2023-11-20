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
Module for defining a Dask executor that submits the input python function in a dask cluster
and waits for execution to finish then returns the result.

This is a plugin executor module; it is loaded if found and properly structured.
"""

import asyncio
import json
import os
from enum import Enum
from typing import Any, Callable, Dict, List, Literal, Optional

from dask.distributed import CancelledError, Client, Future
from pydantic import BaseModel

from covalent._shared_files import TaskRuntimeError, logger

# Relative imports are not allowed in executor plugins
from covalent._shared_files.config import get_config
from covalent._shared_files.exceptions import TaskCancelledError
from covalent._shared_files.util_classes import RESULT_STATUS, Status
from covalent._shared_files.utils import format_server_url
from covalent.executor.base import AsyncBaseExecutor
from covalent.executor.schemas import ResourceMap, TaskSpec, TaskUpdate
from covalent.executor.utils.wrappers import io_wrapper as dask_wrapper
from covalent.executor.utils.wrappers import run_task_from_uris_alt

# The plugin class name must be given by the executor_plugin_name attribute:
EXECUTOR_PLUGIN_NAME = "DaskExecutor"

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

# See https://github.com/dask/distributed/issues/5667
_clients = {}

# See
# https://stackoverflow.com/questions/62164283/why-do-my-dask-futures-get-stuck-in-pending-and-never-finish
_futures = {}

MANAGED_EXECUTION = os.environ.get("COVALENT_USE_OLD_DASK") != "1"

# Dictionary to map Dask clients to their scheduler addresses
_address_client_map = {}


# Valid terminal statuses
class StatusEnum(str, Enum):
    CANCELLED = str(RESULT_STATUS.CANCELLED)
    COMPLETED = str(RESULT_STATUS.COMPLETED)
    FAILED = str(RESULT_STATUS.FAILED)
    READY = "READY"


class ReceiveModel(BaseModel):
    status: StatusEnum


class DaskExecutor(AsyncBaseExecutor):
    """
    Dask executor class that submits the input function to a running LOCAL dask cluster.
    """

    SUPPORTS_MANAGED_EXECUTION = MANAGED_EXECUTION

    def __init__(
        self,
        scheduler_address: str = "",
        log_stdout: str = "stdout.log",
        log_stderr: str = "stderr.log",
        conda_env: str = "",
        cache_dir: str = "",
        current_env_on_conda_fail: bool = False,
        workdir: str = "",
        create_unique_workdir: Optional[bool] = None,
    ) -> None:
        if not cache_dir:
            cache_dir = _EXECUTOR_PLUGIN_DEFAULTS["cache_dir"]

        if not workdir:
            try:
                workdir = get_config("executors.dask.workdir")
            except KeyError:
                workdir = _EXECUTOR_PLUGIN_DEFAULTS["workdir"]
                debug_msg = f"Couldn't find `executors.dask.workdir` in config, using default value {workdir}."
                app_log.debug(debug_msg)

        if create_unique_workdir is None:
            try:
                create_unique_workdir = get_config("executors.dask.create_unique_workdir")
            except KeyError:
                create_unique_workdir = _EXECUTOR_PLUGIN_DEFAULTS["create_unique_workdir"]
                debug_msg = f"Couldn't find `executors.dask.create_unique_workdir` in config, using default value {create_unique_workdir}."
                app_log.debug(debug_msg)

        super().__init__(
            log_stdout,
            log_stderr,
            cache_dir,
            conda_env,
            current_env_on_conda_fail,
        )

        self.workdir = workdir
        self.create_unique_workdir = create_unique_workdir
        self.scheduler_address = scheduler_address

    async def run(self, function: Callable, args: List, kwargs: Dict, task_metadata: Dict):
        """Submit the function and inputs to the dask cluster"""

        if not self.scheduler_address:
            try:
                self.scheduler_address = get_config("dask.scheduler_address")
            except KeyError:
                app_log.debug(
                    "No dask scheduler address found in config. Address must be set manually."
                )

        if await self.get_cancel_requested():
            app_log.debug("Task has cancelled")
            raise TaskCancelledError

        dispatch_id = task_metadata["dispatch_id"]
        node_id = task_metadata["node_id"]

        dask_client = _address_client_map.get(self.scheduler_address)

        if not dask_client:
            dask_client = Client(address=self.scheduler_address, asynchronous=True)
            _address_client_map[self.scheduler_address] = dask_client
            await dask_client

        if self.create_unique_workdir:
            current_workdir = os.path.join(self.workdir, dispatch_id, f"node_{node_id}")
        else:
            current_workdir = self.workdir

        future = dask_client.submit(dask_wrapper, function, args, kwargs, current_workdir)
        await self.set_job_handle(future.key)
        app_log.debug(f"Submitted task {node_id} to dask with key {future.key}")

        try:
            result, worker_stdout, worker_stderr, tb = await future
        except CancelledError as e:
            raise TaskCancelledError() from e

        print(worker_stdout, end="", file=self.task_stdout)
        print(worker_stderr, end="", file=self.task_stderr)

        if tb:
            print(tb, end="", file=self.task_stderr)
            raise TaskRuntimeError(tb)

        # FIX: need to get stdout and stderr from dask worker and print them
        return result

    async def cancel(self, task_metadata: Dict, job_handle) -> Literal[True]:
        """
        Cancel the task being executed by the dask executor currently

        Arg(s)
            task_metadata: Metadata associated with the task
            job_handle: Key assigned to the job by Dask

        Return(s)
            True by default
        """

        if not self.scheduler_address:
            try:
                self.scheduler_address = get_config("dask.scheduler_address")
            except KeyError:
                app_log.debug(
                    "No dask scheduler address found in config. Address must be set manually."
                )

        dask_client = _address_client_map.get(self.scheduler_address)

        if not dask_client:
            dask_client = Client(address=self.scheduler_address, asynchronous=True)
            await asyncio.wait_for(dask_client, timeout=5)

        fut: Future = Future(key=job_handle, client=dask_client)

        # https://stackoverflow.com/questions/46278692/dask-distributed-how-to-cancel-tasks-submitted-with-fire-and-forget
        await dask_client.cancel([fut], asynchronous=True, force=True)
        app_log.debug(f"Cancelled future with key {job_handle}")
        return True

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

        if not self.scheduler_address:
            try:
                self.scheduler_address = get_config("dask.scheduler_address")
            except KeyError:
                app_log.debug(
                    "No dask scheduler address found in config. Address must be set manually."
                )

        dask_client = Client(address=self.scheduler_address, asynchronous=True)
        await asyncio.wait_for(dask_client, timeout=5)

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

        key = f"dask_job_{dispatch_id}:{gid}"

        await self.set_job_handle(key)

        future = dask_client.submit(
            run_task_from_uris_alt,
            list(map(lambda t: t.model_dump(), task_specs)),
            resources.model_dump(),
            output_uris,
            self.cache_dir,
            task_group_metadata,
            server_url,
            key=key,
        )

        _clients[key] = dask_client
        _futures[key] = future

        return future.key

    async def poll(self, task_group_metadata: Dict, poll_data: Any):
        fut = _futures.pop(poll_data)
        app_log.debug(f"Future {fut}")
        try:
            await fut
        except CancelledError as e:
            raise TaskCancelledError() from e

        _clients.pop(poll_data)

        return {"status": StatusEnum.READY.value}

    async def receive(self, task_group_metadata: Dict, data: Any) -> List[TaskUpdate]:
        # Job should have reached a terminal state by the time this is invoked.
        dispatch_id = task_group_metadata["dispatch_id"]
        task_ids = task_group_metadata["node_ids"]

        task_results = []

        if not data:
            terminal_status = RESULT_STATUS.CANCELLED
        else:
            received = ReceiveModel.model_validate(data)
            terminal_status = Status(received.status.value)

        for task_id in task_ids:
            # TODO: Handle the case where the job was cancelled before the task started running
            app_log.debug(f"Receive called for task {dispatch_id}:{task_id} with data {data}")

            if terminal_status == RESULT_STATUS.CANCELLED:
                output_uri = ""
                stdout_uri = ""
                stderr_uri = ""
                qelectron_db_uri = ""

            else:
                result_path = os.path.join(self.cache_dir, f"result-{dispatch_id}:{task_id}.json")
                with open(result_path, "r") as f:
                    result_summary = json.load(f)
                    node_id = result_summary["node_id"]
                    output_uri = result_summary["output_uri"]
                    stdout_uri = result_summary["stdout_uri"]
                    stderr_uri = result_summary["stderr_uri"]
                    qelectron_db_uri = result_summary["qelectron_db_uri"]
                    exception_raised = result_summary["exception_occurred"]

                terminal_status = (
                    RESULT_STATUS.FAILED if exception_raised else RESULT_STATUS.COMPLETED
                )

            task_result = {
                "dispatch_id": dispatch_id,
                "node_id": task_id,
                "status": terminal_status,
                "assets": {
                    "output": {
                        "remote_uri": output_uri,
                    },
                    "stdout": {
                        "remote_uri": stdout_uri,
                    },
                    "stderr": {
                        "remote_uri": stderr_uri,
                    },
                    "qelectron_db": {
                        "remote_uri": qelectron_db_uri,
                    },
                },
            }

            task_results.append(TaskUpdate(**task_result))

        app_log.debug(f"Returning results for tasks {dispatch_id}:{task_ids}")
        return task_results

    def get_upload_uri(self, task_group_metadata: Dict, object_key: str):
        dispatch_id = task_group_metadata["dispatch_id"]
        task_group_id = task_group_metadata["task_group_id"]

        filename = f"asset_{dispatch_id}-{task_group_id}_{object_key}.pkl"
        return os.path.join("file://", self.cache_dir, filename)
