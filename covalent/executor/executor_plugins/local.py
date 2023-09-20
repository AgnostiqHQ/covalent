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


import os
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Callable, Dict, List

# Relative imports are not allowed in executor plugins
from covalent._shared_files import TaskCancelledError, TaskRuntimeError, logger
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

        # Run the target function in a separate process
        fut = proc_pool.submit(io_wrapper, function, args, kwargs)

        output, worker_stdout, worker_stderr, tb = fut.result()

        print(worker_stdout, end="", file=self.task_stdout)
        print(worker_stderr, end="", file=self.task_stderr)

        if tb:
            print(tb, end="", file=self.task_stderr)
            raise TaskRuntimeError(tb)

        return output
