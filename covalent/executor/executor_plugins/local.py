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
from typing import Any, Callable, Dict, List, Optional

# Relative imports are not allowed in executor plugins
from covalent._shared_files import TaskCancelledError, TaskRuntimeError, logger
from covalent._shared_files.config import get_config
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
    "workdir": os.path.join(
        os.environ.get("XDG_CACHE_HOME") or os.path.join(os.environ["HOME"], ".cache"),
        "covalent",
        "workdir",
    ),
    "create_unique_workdir": False,
}


proc_pool = ProcessPoolExecutor()


class LocalExecutor(BaseExecutor):
    """
    Local executor class that directly invokes the input function.
    """

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
