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
Module for defining a Dask executor that submits the input python function in a dask cluster
and waits for execution to finish then returns the result.

This is a plugin executor module; it is loaded if found and properly structured.
"""

import json
import os
from typing import Any, Callable, Dict, List

from dask.distributed import Client, fire_and_forget

from covalent._shared_files import TaskRuntimeError, logger

# Relative imports are not allowed in executor plugins
from covalent._shared_files.config import get_config
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._shared_files.utils import _address_client_mapper
from covalent.executor.base import AsyncBaseExecutor
from covalent.executor.utils.wrappers import io_wrapper as dask_wrapper
from covalent.executor.utils.wrappers import run_task_from_uris

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
}

MANAGED_EXECUTION = os.environ.get("COVALENT_USE_MANAGED_DASK") == "1"


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
        cache_dir: str = "",
        current_env_on_conda_fail: bool = False,
        time_limit: int = 600,
    ) -> None:
        if not cache_dir:
            cache_dir = os.path.join(
                os.environ.get("XDG_CACHE_HOME") or os.path.join(os.environ["HOME"], ".cache"),
                "covalent",
            )

        if not scheduler_address:
            try:
                scheduler_address = get_config("dask.scheduler_address")
            except KeyError as ex:
                app_log.debug(
                    "No dask scheduler address found in config. Address must be set manually."
                )

        super().__init__(log_stdout, log_stderr, cache_dir=cache_dir)

        self.scheduler_address = scheduler_address
        self.time_limit = time_limit

    async def run(self, function: Callable, args: List, kwargs: Dict, task_metadata: Dict):
        """Submit the function and inputs to the dask cluster"""

        node_id = task_metadata["node_id"]

        dask_client = _address_client_mapper.get(self.scheduler_address)

        if not dask_client:
            dask_client = Client(address=self.scheduler_address, asynchronous=True)
            _address_client_mapper[self.scheduler_address] = dask_client

            await dask_client

        future = dask_client.submit(dask_wrapper, function, args, kwargs)
        app_log.debug(f"Submitted task {node_id} to dask")

        result, worker_stdout, worker_stderr, tb = await future

        print(worker_stdout, end="", file=self.task_stdout)
        print(worker_stderr, end="", file=self.task_stderr)

        if tb:
            print(tb, end="", file=self.task_stderr)
            raise TaskRuntimeError(tb)

        # FIX: need to get stdout and stderr from dask worker and print them
        return result

    async def send(
        self,
        task_specs: List[Dict],
        resources: dict,
        task_group_metadata: dict,
    ):
        # Assets are assumed to be accessible by the compute backend
        # at the provided URIs

        # The Asset Manager is responsible for uploading all assets
        # Returns a job handle (should be JSONable)

        dask_client = Client(address=self.scheduler_address, asynchronous=True)
        await dask_client

        dispatch_id = task_group_metadata["dispatch_id"]
        task_ids = task_group_metadata["task_ids"]
        gid = task_group_metadata["task_group_id"]
        output_uris = []
        for node_id in task_ids:
            result_uri = os.path.join(self.cache_dir, f"result_{dispatch_id}-{node_id}.pkl")
            stdout_uri = os.path.join(self.cache_dir, f"stdout_{dispatch_id}-{node_id}.txt")
            stderr_uri = os.path.join(self.cache_dir, f"stderr_{dispatch_id}-{node_id}.txt")
            output_uris.append((result_uri, stdout_uri, stderr_uri))
        # future = dask_client.submit(lambda x: x**3, 3)

        dispatcher_addr = get_config("dispatcher.address")
        dispatcher_port = get_config("dispatcher.port")
        server_url = f"http://{dispatcher_addr}:{dispatcher_port}"
        key = f"dask_job_{dispatch_id}:{gid}"
        future = dask_client.submit(
            run_task_from_uris,
            task_specs,
            resources,
            output_uris,
            self.cache_dir,
            task_group_metadata,
            server_url,
            key=key,
        )

        fire_and_forget(future)

        app_log.debug(f"Fire and forgetting task group {dispatch_id}:{gid}")

        return future.key

    async def poll(self, task_group_metadata: Dict, job_handle: Any):

        return -1

    async def receive(self, task_group_metadata: Dict, job_handle: Any):

        # Returns (output_uri, stdout_uri, stderr_uri,
        # exception_raised)

        # Job should have reached a terminal state by the time this is invoked.
        dispatch_id = task_group_metadata["dispatch_id"]
        task_ids = task_group_metadata["task_ids"]

        task_results = []

        for task_id in task_ids:
            result_path = os.path.join(self.cache_dir, f"result-{dispatch_id}:{task_id}.json")
            with open(result_path, "r") as f:
                result_summary = json.load(f)
                node_id = result_summary["node_id"]
                output_uri = result_summary["output_uri"]
                stdout_uri = result_summary["stdout_uri"]
                stderr_uri = result_summary["stderr_uri"]
                exception_raised = result_summary["exception_occurred"]

                terminal_status = (
                    RESULT_STATUS.FAILED if exception_raised else RESULT_STATUS.COMPLETED
                )

                task_result = {
                    "dispatch_id": dispatch_id,
                    "node_id": node_id,
                    "output_uri": output_uri,
                    "stdout_uri": stdout_uri,
                    "stderr_uri": stderr_uri,
                    "status": terminal_status,
                }
                task_results.append(task_result)

        app_log.debug(f"Returning results for tasks {dispatch_id}:{task_ids}")
        return task_results

    def get_upload_uri(self, task_group_metadata: Dict, object_key: str):
        # dispatch_id = task_group_metadata["dispatch_id"]
        # task_group_id = task_group_metadata["task_group_id"]

        # filename = f"asset_{dispatch_id}-{task_group_id}_{object_key}.pkl"
        # return os.path.join("file://", self.cache_dir, filename)
        return ""
