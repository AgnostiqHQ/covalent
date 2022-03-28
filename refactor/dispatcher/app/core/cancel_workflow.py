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

import os
from typing import List, Tuple

import requests
from dotenv import load_dotenv

from covalent._results_manager import Result

from .dispatch_workflow import get_result_object_from_result_service
from .utils import is_sublattice

load_dotenv()


BASE_URI = os.environ.get("BASE_URI")


def cancel_workflow_execution(
    result_obj: Result, task_id_batch: List[Tuple[str, int]] = None
) -> bool:
    """Main cancel function. Called by the user via ct.cancel(dispatch_id). The task_id_batch is composed of both
    dispatch id and task ids in the form of a tuple."""

    cancellation_status = True

    tasks = get_all_task_ids(result_obj) if not task_id_batch else task_id_batch

    for dispatch_id, task_id in tasks:
        if not cancel_task(dispatch_id, task_id):
            cancellation_status = False

    return cancellation_status


def cancel_task(dispatch_id: str, task_id: int) -> bool:
    """Asks the Runner API to cancel the execution of these tasks and returns the status of whether it was
    successful."""

    resp = requests.delete(f"{BASE_URI}/api/v0/workflow/{dispatch_id}/task/{task_id}/cancel")
    if (
        ("cancelled_dispatch_id" and "cancelled_task_id" in resp.json())
        and (resp.json()["cancelled_dispatch_id"] == dispatch_id)
        and (resp.json()["cancelled_task_id"] == task_id)
    ):
        return True

    return False


def get_all_task_ids(result_obj: Result) -> List[Tuple[str, int]]:
    """Get all the task ids and the corresponding dispatch ids for a given lattice. When a sublattice is encountered,
    the dispatch iud corresponding to the sublattice `dispatch_id:task_id` is used."""

    task_ids = []
    for task_id in range(result_obj._num_nodes):
        task_name = result_obj.lattice.transport_graph.get_node_value(task_id, "name")
        if not is_sublattice(task_name):
            task_ids.append((result_obj.dispatch_id, task_id))
        else:
            sublattice_result_obj = get_result_object_from_result_service(
                f"{result_obj.dispatch_id}:{task_id}"
            )
            task_ids += get_all_task_ids(sublattice_result_obj)

    return task_ids
