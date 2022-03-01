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

import os
from multiprocessing import Pool

from .base_runner import BaseRunner


class MultiProcRunner(BaseRunner):
    def __init__(self):
        self.available_resources = os.cpu_count() - 1
        self.process_pool = None

    def begin(self, list_of_tasks):
        self.process_pool = Pool(processes=self.available_resources)

        for task in list_of_tasks:
            self.process_pool.apply_async(
                func=self.run_new_task,
                args=(task["node_id"], task["func"], task["args"], task["kwargs"]),
            )
            self.available_resources -= 1

    @staticmethod
    def run_new_task(node_id, task_func, task_args, task_kwargs):

        # Start the new task
        pass

    def cancel_task(self, node_id):

        # Cancel the task

        self.available_resources += 1

    def query_task_status(self, node_id):
        pass

    @staticmethod
    def task_callback(result):

        # Callback once the task is complete
        pass

    @staticmethod
    def task_error_callback(resukt):

        # Callback if task failed
        pass


if __name__ == "__main__":

    # Make sure if creating new process, then it should be called within this `if` block.
    pass
