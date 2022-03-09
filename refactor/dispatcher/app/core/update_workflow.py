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

from .utils import _post_process, is_workflow_completed, update_ui


def update_workflow(task_execution_results: Dict, result_obj: Result) -> Result:
    """Main update function. Called by the Runner API when there is an update for task
    execution status."""

    # Update the task results
    result_obj._update_node(**task_execution_results)
    update_ui(result_obj=result_obj)

    # If workflow is completed, post-process result
    if is_workflow_completed(result_obj=result_obj):

        task_execution_order: List[
            List
        ] = result_obj.lattice.transport_graph.get_topologically_sorted_graph()

        result_obj._result = _post_process(
            lattice=result_obj.lattice,
            task_outputs=result_obj.get_all_node_outputs(),
            task_execution_order=task_execution_order,
        )

        result_obj._status = Result.COMPLETED
        result_obj._end_time = datetime.now(timezone.utc)

        update_ui(result_obj=result_obj)

    return result_obj
