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

import multiprocessing as mp
import os
from typing import Callable, Dict, List

# Relative imports are not allowed in executor plugins
from covalent._shared_files import TaskRuntimeError, logger
from covalent.executor import BaseExecutor

# Store the wrapper function in an external module to avoid module
# import errors during pickling
from covalent.executor.utils.wrappers import local_wrapper

# The plugin class name must be given by the executor_plugin_name attribute:
EXECUTOR_PLUGIN_NAME = "LocalExecutor"

# Platform enums for determening multiprocessing start mode
PLATFORM_DARWIN = "Darwin"

app_log = logger.app_log
log_stack_info = logger.log_stack_info

_EXECUTOR_PLUGIN_DEFAULTS = {
    "log_stdout": "stdout.log",
    "log_stderr": "stderr.log",
    "cache_dir": os.path.join(
        os.environ.get("XDG_CACHE_HOME") or os.path.join(os.environ["HOME"], ".cache"), "covalent"
    ),
}


# try:
#     #app_log.debug("Setting ")
#     print("Setting start method")
#     mp.set_start_method('fork',)
# except RuntimeError as e:
#     print(e)
#     pass


class LocalExecutor(BaseExecutor):
    """
    Local executor class that directly invokes the input function.
    """

    def run(self, function: Callable, args: List, kwargs: Dict, task_metadata: Dict):
        app_log.debug(f"Running function {function} locally")
        q = mp.Queue()

        print(f"Using start method: {mp.get_start_method()}")
        # Run the target function in a separate process
        proc = mp.Process(target=local_wrapper, args=(function, args, kwargs, q))
        proc.start()
        proc.join()
        output, worker_stdout, worker_stderr, tb = q.get(False)

        print(worker_stdout, end="", file=self.task_stdout)
        print(worker_stderr, end="", file=self.task_stderr)

        if tb:
            print(tb, end="", file=self.task_stderr)
            raise TaskRuntimeError(tb)

        return output
