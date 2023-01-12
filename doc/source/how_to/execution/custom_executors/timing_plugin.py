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


import time
from pathlib import Path
from typing import Callable, Dict, List

from covalent.executor import BaseExecutor

executor_plugin_name = "TimingExecutor"
_EXECUTOR_PLUGIN_DEFAULTS = {"timing_filepath": ""}


class TimingExecutor(BaseExecutor):
    def __init__(self, timing_filepath, **kwargs):
        self.timing_filepath = str(Path(timing_filepath).resolve())
        super().__init__(**kwargs)

    def run(self, function: Callable, args: List, kwargs: Dict, task_metadata: Dict):

        start = time.process_time()

        result = function(*args, **kwargs)

        time_taken = time.process_time() - start

        with open(f"{self.timing_filepath}", "a") as f:
            f.writelines(
                f"Node {task_metadata['node_id']} in dispatch {task_metadata['dispatch_id']} took {time_taken}s of CPU time."
            )

        return result
