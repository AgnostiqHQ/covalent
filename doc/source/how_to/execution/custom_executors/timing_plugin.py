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


"""Timing executor plugin for Covalent."""

import time
from pathlib import Path
from typing import Any, Callable, Dict, List

from covalent.executor.base import BaseExecutor

executor_plugin_name = "TimingExecutor"  # Required by covalent.executors

_EXECUTOR_PLUGIN_DEFAULTS = {
    "timing_filepath": ""
}  # Set default values for executor plugin parameters here


class TimingExecutor(BaseExecutor):
    """Executor that times the execution time."""

    def __init__(self, timing_filepath: str = "", **kwargs):
        """Init function.

        Args:
            timing_filepath: Filepath where the timing information will be written.

        """
        self.timing_filepath = str(Path(timing_filepath).resolve())
        super().__init__(**kwargs)

    def run(self, function: Callable, args: List, kwargs: Dict, task_metadata: Dict) -> Any:
        """Measures the time taken to execute a function.

        Args:
            function: Function to be executed.
            args: Arguments to be passed to the function.
            kwargs: Keyword arguments to be passed to the function.
            task_metadata: Metadata about the task. Expects node_id and dispatch_id.

        Returns:
            The result of the function.

        """
        start = time.process_time()

        result = function(*args, **kwargs)

        time_taken = time.process_time() - start

        with open(f"{self.timing_filepath}", "w") as f:
            f.write(
                f"Node {task_metadata['node_id']} in dispatch {task_metadata['dispatch_id']} took {time_taken}s of CPU time.\n"
            )

        return result
