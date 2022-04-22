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

"""Workflow cancel functionality."""

import sys
from datetime import datetime, timezone
from typing import List, Tuple

from app.core.get_svc_uri import RunnerURI
from app.core.utils import (
    generate_task_result,
    get_parent_id_and_task_id,
    get_result_object_from_result_service,
    is_sublattice,
    is_sublattice_dispatch_id,
    send_cancel_task_to_runner,
    send_result_object_to_result_service,
    send_task_update_to_dispatcher,
)

from covalent._results_manager import Result


def cancel_workflow_execution(
    result_obj: Result, task_id_batch: List[Tuple[str, int]] = None
) -> bool:
    """Main cancel function. Called by the user via ct.cancel(dispatch_id). The task_id_batch is composed of both
    dispatch id and task ids in the form of a tuple."""

    workflow_cancelled = True

    (
        dispatch_and_task_id_lot,
        unrun_tasks_lot,
    ) = task_id_batch or get_cancellable_dispatch_and_task_ids(result_obj)

    # Using the cancellation_status variable because we still want to continue
    # attempting cancellation of further tasks even if one of them has failed
    for dispatch_id, task_id in dispatch_and_task_id_lot:
        task_cancelled = cancel_task(dispatch_id, task_id)

        if is_sublattice_dispatch_id(dispatch_id) and task_cancelled:
            parent_dispatch_id, task_id = get_parent_id_and_task_id(dispatch_id)

            task_result = generate_task_result(
                task_id=task_id,
                end_time=datetime.now(timezone.utc),
                status=Result.CANCELLED,
            )

            send_task_update_to_dispatcher(parent_dispatch_id, task_result)

        if not task_cancelled:
            workflow_cancelled = False

    if workflow_cancelled and not task_id_batch:
        for dispatch_id, task_id in unrun_tasks_lot:
            cancel_unrun_tasks(dispatch_id, task_id)

    print(f"Cancelled workflow: {workflow_cancelled}", file=sys.stderr)

    return workflow_cancelled


def cancel_unrun_tasks(dispatch_id: str, task_id: int) -> None:

    task_result = generate_task_result(
        task_id=task_id,
        end_time=datetime.now(timezone.utc),
        status=Result.CANCELLED,
    )

    send_task_update_to_dispatcher(dispatch_id, task_result)


def cancel_task(dispatch_id: str, task_id: int) -> bool:
    """Asks the Runner API to cancel the execution of these tasks and returns the status of whether it was
    successful."""

    cancelled_dispatch_id, cancelled_task_id = send_cancel_task_to_runner(
        dispatch_id=dispatch_id, task_id=task_id
    )
    print(
        f"Cancel dispatch id: {type(cancelled_dispatch_id)}, cancel task id: {type(cancelled_task_id)}",
        file=sys.stderr,
    )
    if (
        (cancelled_dispatch_id and cancelled_task_id)
        and (cancelled_dispatch_id == dispatch_id)
        and (cancelled_task_id == str(task_id))
    ):
        return True

    return False


def get_cancellable_dispatch_and_task_ids(result_obj: Result) -> List[Tuple[str, int]]:
    """Get all the task ids and the corresponding dispatch ids for a given lattice. When a sublattice is encountered,
    the dispatch id corresponding to the sublattice `dispatch_id:task_id` is used."""

    dispatch_and_task_id_lot = []
    unrun_tasks_lot = []

    task_order = result_obj.transport_graph.get_topologically_sorted_graph()
    task_ids = [id for sublist in task_order for id in sublist]

    for task_id in task_ids:

        if result_obj._get_node_status(task_id) == Result.RUNNING:
            lot_to_update = dispatch_and_task_id_lot

        elif result_obj._get_node_status(task_id) == Result.NEW_OBJ:
            lot_to_update = unrun_tasks_lot

        else:
            continue

        task_name = result_obj._get_node_name(task_id)
        if not is_sublattice(task_name):
            lot_to_update.append((result_obj.dispatch_id, task_id))
        else:

            # Super lattice's sublattice task needs to get cancelled
            # too right here
            unrun_tasks_lot.append((result_obj.dispatch_id, task_id))

            sublattice_result_obj = get_result_object_from_result_service(
                f"{result_obj.dispatch_id}:{task_id}"
            )
            lot_1, lot_2 = get_cancellable_dispatch_and_task_ids(sublattice_result_obj)

            dispatch_and_task_id_lot = lot_1 + dispatch_and_task_id_lot
            unrun_tasks_lot = lot_2 + unrun_tasks_lot

    return dispatch_and_task_id_lot, unrun_tasks_lot
