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
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List

# Relative imports are not allowed in executor plugins
from covalent._shared_files import logger
from covalent.executor import BaseExecutor, wrapper_fn  # nopycln: import

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


class LocalExecutor(BaseExecutor):
    """
    Local executor class that directly invokes the input function.
    """

    def setup(self, task_metadata: Dict = {}):
        app_log.debug(f"Local executor {self.instance_id}: spinning up worker thread")
        resources = {"threadpool": ThreadPoolExecutor(max_workers=1)}
        return resources

    def teardown(self, resource_data: Dict = {}):
        threadpool = resource_data["threadpool"]
        threadpool.shutdown()
        app_log.debug(f"Local executor {self.instance_id}: shut down worker thread")

    def run(self, function: Callable, args: List, kwargs: Dict, task_metadata: Dict):
        app_log.debug(f"Local executor {self.instance_id}: {self._tasks_left} tasks left")
        app_log.debug(f"Running function {function} locally")
        dispatch_id = task_metadata["dispatch_id"]
        node_id = task_metadata["node_id"]
        threadpool = self._get_resource_data()["threadpool"]

        if self._get_task_status(dispatch_id, node_id) == "RUNNING":
            fut = threadpool.submit(function, *args, **kwargs)
            self._set_task_data(dispatch_id, node_id, "future", fut)
        else:
            raise RuntimeError("Job has been cancelled")
        return fut.result()

    def cancel(self, dispatch_id: str, node_id: int):
        fut = self._get_task_data(dispatch_id, node_id, "future")
        if fut:
            app_log.debug(f"Cancelling future for task {dispatch_id}:{node_id}")
            fut.cancel()
            app_log.debug(f"Cancelled future for task {dispatch_id}:{node_id}")
