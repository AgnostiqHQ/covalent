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

from typing import Dict

from covalent._results_manager import Result
from covalent._workflow.transport import _TransportGraph


def is_workflow_running(dispatch_id: int) -> bool:
    """Check if workflow is running."""

    pass


def is_workflow_completed(dispatch_id: int) -> bool:
    """Check if workflow is completed"""

    pass


def is_task_completed(dispatch_id: int) -> bool:
    """Check if task is completed."""

    pass


def cancel_workflow():
    """Cancel the workflow."""

    pass


def update_workflow(task_execution_result: Dict, result_object: Result):
    """Update the workflow with task execution results."""

    result_object._update_node(**task_execution_result)


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
