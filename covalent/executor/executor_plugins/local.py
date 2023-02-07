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
Module for defining a local executor that directly invokes the input python function.

This is a plugin executor module; it is loaded if found and properly structured.
"""

import asyncio
import json
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Callable, Dict, List

# Relative imports are not allowed in executor plugins
from covalent._shared_files import TaskRuntimeError, logger
from covalent._shared_files.config import get_config
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent.executor import BaseExecutor

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
}

proc_pool = ProcessPoolExecutor()


class LocalExecutor(BaseExecutor):
    """
    Local executor class that directly invokes the input function.
    """

    SUPPORTS_MANAGED_EXECUTION = True

    def run(self, function: Callable, args: List, kwargs: Dict, task_metadata: Dict):
        app_log.debug(f"Running function {function} locally")

        # Run the target function in a separate process
        fut = proc_pool.submit(io_wrapper, function, args, kwargs)

        output, worker_stdout, worker_stderr, tb = fut.result()

        print(worker_stdout, end="", file=self.task_stdout)
        print(worker_stderr, end="", file=self.task_stderr)

        if tb:
            print(tb, end="", file=self.task_stderr)
            raise TaskRuntimeError(tb)

        return output

    def _send(
        self,
        task_specs: List[Dict],
        resources: dict,
        task_group_metadata: dict,
    ):

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
        future = proc_pool.submit(
            run_task_from_uris,
            task_specs,
            resources,
            output_uris,
            self.cache_dir,
            task_group_metadata,
            server_url,
        )
        return 42

    def _receive(self, task_group_metadata: Dict, job_handle: Any):

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

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self._send,
            task_specs,
            resources,
            task_group_metadata,
        )

    async def poll(self, task_group_metadata: Dict, job_handle: Any):

        # To be run as a background task.  A callback will be
        # registered with the runner to invoke the receive()

        return -1

    async def receive(self, task_group_metadata: Dict, job_handle: Any):

        # Returns (output_uri, stdout_uri, stderr_uri,
        # exception_raised)

        # Job should have reached a terminal state by the time this is invoked.
        loop = asyncio.get_running_loop()

        return await loop.run_in_executor(
            None,
            self._receive,
            task_group_metadata,
            job_handle,
        )

    def get_upload_uri(self, task_group_metadata: Dict, object_key: str):
        return ""
