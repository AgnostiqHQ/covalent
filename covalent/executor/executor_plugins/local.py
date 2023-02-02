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


import os
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Callable, Dict, List

# Relative imports are not allowed in executor plugins
from covalent._shared_files import TaskRuntimeError, logger
from covalent.executor import BaseExecutor

# Store the wrapper function in an external module to avoid module
# import errors during pickling
from covalent.executor.utils.wrappers import io_wrapper

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

    async def send(
        self,
        function_uri: str,
        deps_uri: str,
        call_before_uri: str,
        call_after_uri: str,
        args_uris: str,
        kwargs_uris: str,
        task_metadata: dict,
    ):
        # Assets are assumed to be accessible by the compute backend
        # at the provided URIs

        # The Asset Manager is responsible for uploading all assets
        # Returns a job handle (should be JSONable)

        raise NotImplementedError

    async def poll(self, task_metadata: Dict, job_handle: Any):

        # To be run as a background task.  A callback will be
        # registered with the runner to invoke the receive()

        return -1

    async def receive(self, task_metadata: Dict, job_handle: Any):

        # Returns (output_uri, stdout_uri, stderr_uri,
        # exception_raised)

        # Job should have reached a terminal state by the time this is invoked.

        raise NotImplementedError

    def get_upload_uri(self, task_metadata: Dict, object_key: str):
        return ""
