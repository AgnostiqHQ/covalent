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

"""Runtime utility classes for the executor"""

import asyncio

import covalent.executor.base
from covalent._results_manager.result import Result
from covalent._shared_files.defaults import parameter_prefix


class ExecutorCache:
    """Dispatcher cache of live executor instances"""

    def __init__(self, result_object: Result = None):
        self.id_instance_map = {}
        self.tasks_per_instance = {}

        if result_object:
            self.initialize_from_result_object(result_object)

    def initialize_from_result_object(self, result_object: Result):
        g = result_object.lattice.transport_graph

        for node in g._graph.nodes:
            node_name = result_object.lattice.transport_graph.get_node_value(node, "name")

            # Skip parameter nodes since they don't run in an executor
            if node_name.startswith(parameter_prefix):
                continue
            executor_data = g.get_node_value(node, "metadata")["executor_data"]

            # DEBUGGING ONLY: This should never happen
            if not executor_data:
                assert False

            executor_id = executor_data["attributes"]["instance_id"]

            self.id_instance_map[executor_id] = None
            if executor_id not in self.tasks_per_instance:
                self.tasks_per_instance[executor_id] = 1
            else:
                self.tasks_per_instance[executor_id] += 1

        # Do the same for postprocessing (if postprocessing is still around:) )
        executor_data = result_object.lattice.get_metadata("workflow_executor_data")
        if executor_data:
            executor_id = executor_data["attributes"]["instance_id"]

            self.id_instance_map[executor_id] = None
            if executor_id not in self.tasks_per_instance:
                self.tasks_per_instance[executor_id] = 1
            else:
                self.tasks_per_instance[executor_id] += 1

    # Might be better to bring back the info_queue and just send a
    # "cleanup" message
    async def finalize_executors(self):
        """Clean up any executors still running"""
        for key, executor in self.id_instance_map.items():
            if executor is None:
                continue
            if isinstance(executor, covalent.executor.base.AsyncBaseExecutor):
                await executor.teardown()
            else:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, executor.teardown)
