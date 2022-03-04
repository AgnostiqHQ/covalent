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

from datetime import datetime, timezone
from typing import Dict, List

from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import _TransportGraph


def is_workflow_running(result_object: Result) -> bool:
    """Check if workflow is running."""

    return result_object.status == "RUNNING"


def is_workflow_completed(result_object: Result) -> bool:
    """Check if workflow is completed"""

    # TODO - Clarify if FAILED status belongs here
    return result_object == "COMPLETED" or "FAILED"


def is_task_completed(task_id: int, result_object: Result) -> bool:
    """Check if task is completed."""

    # TODO - Refactor `node_id` -> `task_id`
    # TODO - Clarify if FAILED status belongs here
    return result_object.get_node_status(task_id=task_id) == "COMPLETED" or "FAILED"


def cancel_workflow():
    """Cancel the workflow."""

    pass


def update_task_results(task_execution_result: Dict, result_object: Result):
    """Update the workflow with task execution results."""

    result_object._update_node(**task_execution_result)


def _post_process(lattice: Lattice, node_outputs: Dict, task_exec_order: List[List]):
    """TODO - Describe post processing here."""

    return "workflow_result"


def update_workflow_results(workflow_execution_result: Dict, result_object: Result):
    """Update workflow results"""

    # TODO - This might be a very central component; consider in more detail
    order = result_object.lattice.transport_graph.get_topologically_sorted_graph()

    # post process the lattice
    result_object._result = _post_process(
        result_object.lattice, result_object.get_all_node_outputs(), order
    )

    result_object._status = Result.COMPLETED
    result_object._end_time = datetime.now(timezone.utc)

    # TODO - Double check that this is indeed equivalent to writing to the database
    result_object.save()


def run_workflow():
    pass


def dispatch_workflow(result_object: Result) -> None:
    """If workflow is not running, i.e. just picked up from the queue, run dispatcher."""

    # TODO - Consider having a result_object.copy_transport_graph() method.
    # TODO - Consider creating a method to carry out the functionality below.
    transport_graph = _TransportGraph()
    transport_graph.deserialize(result_object.lattice.transport_graph)
    result_object._lattice.transport_graph = transport_graph
    result_object._initialize_nodes()

    result_object.save()  # Not sure what this does or why it's necessary. Assuming this is
    # writing the result object update to the database. We might not want to constantly read and
    # write.

    run_workflow()
