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


from multiprocessing import Queue as MPQ
from typing import Any, List

import cloudpickle as pickle
from app.core.cancel_workflow import cancel_workflow_execution
from app.core.dispatch_workflow import dispatch_workflow
from app.core.dispatcher_logger import logger
from app.core.update_workflow import update_workflow_results
from app.core.utils import (
    get_result_object_from_result_service,
    is_empty,
    is_sublattice_dispatch_id,
    update_result_and_ui,
)
from app.schemas.workflow import (
    BatchCancelWorkflowResponse,
    CancelWorkflowResponse,
    DispatchWorkflowResponse,
    UpdateWorkflowResponse,
)
from fastapi import APIRouter, File, Query

from covalent._results_manager import Result

workflow_tasks_queue = MPQ()
workflow_status_queue = MPQ()

# Using sentinel to indicate that the queue is empty since MPQ.empty() is an unreliable method
workflow_tasks_queue.put(None)
workflow_status_queue.put(None)


router = APIRouter()

# Do we need this here?
mock_result = {
    "status": "COMPLETED",
    "result": {
        "dispatch_id": "",
        "results_dir": "",
        "status": "COMPLETED",
        "graph": {
            "links": [{"edge_name": "data", "param_type": "kwarg", "source": 0, "target": 1}],
            "nodes": [
                {
                    "name": "load_data",
                    "metadata": {"executor": "<LocalExecutor>"},
                    "function_string": "@ct.electron\ndef load_data():\n    iris = datasets.load_iris()\n    perm = permutation(iris.target.size)\n    iris.data = iris.data[perm]\n    iris.target = iris.target[perm]\n    return iris.data, iris.target\n\n\n",
                    "start_time": "2022-02-28T23:21:17.844268+00:00",
                    "end_time": "2022-02-28T23:21:17.853741+00:00",
                    "status": "COMPLETED",
                    "output": ["[[5.  3.4 1.5 0.2]]"],
                    "error": None,
                    "sublattice_result": None,
                    "stdout": "",
                    "stderr": "",
                    "id": 0,
                    "doc": None,
                    "kwargs": None,
                }
            ],
        },
    },
}


logger.warning("Dispatcher Service Started")


@router.post("/{dispatch_id}", status_code=202, response_model=DispatchWorkflowResponse)
def submit_workflow(*, dispatch_id: str) -> Any:
    """
    Submit a workflow
    """

    logger.warning(f"Inside submit_workflow with dispatch_id: {dispatch_id}")

    # Change workflow status to RUNNING
    workflow_status_queue.get()

    workflow_status_queue.put(Result.RUNNING)

    # Get the result object
    result_obj = get_result_object_from_result_service(dispatch_id=dispatch_id)

    # Dispatch the workflow
    dispatch_workflow(result_obj=result_obj, tasks_queue=workflow_tasks_queue)

    vv = workflow_tasks_queue.get()

    logger.warning(f"IT SHOULD NOT BE EMPTY HERE {vv}")

    workflow_tasks_queue.put(vv)

    logger.warning(f"Inside submit_workflow dispatching done with dispatch_id: {dispatch_id}")

    return {"response": f"{dispatch_id} workflow dispatched successfully"}


@router.delete("/{dispatch_id}", status_code=200, response_model=CancelWorkflowResponse)
def cancel_workflow(*, dispatch_id: str) -> CancelWorkflowResponse:
    """
    Cancel a workflow
    """

    result_obj = get_result_object_from_result_service(dispatch_id=dispatch_id)

    success = cancel_workflow_execution(result_obj)

    # Note - The queue should be populated in theory.
    if not is_empty(workflow_tasks_queue):
        workflow_tasks_queue.get()
        workflow_tasks_queue.put(None)

    # Empty queue when workflow is terminated
    if success:
        workflow_status_queue.get()
        workflow_status_queue.put(None)

        return {"response": f"{dispatch_id} workflow cancelled successfully"}
    else:
        return {"response": f"{dispatch_id} workflow did not cancel successfully"}


@router.delete("/cancel", status_code=200, response_model=BatchCancelWorkflowResponse)
def cancel_workflows(*, dispatch_ids: List[str] = Query([])) -> BatchCancelWorkflowResponse:
    """
    Cancel a set of workflows
    """

    # Mock response here
    mock_response = {
        "cancelled": ["string"],
        "failed": ["string"],
    }

    return mock_response


@router.put("/{dispatch_id}", status_code=200, response_model=UpdateWorkflowResponse)
def update_workflow(
    *, dispatch_id: str, task_execution_results: bytes = File(...)
) -> UpdateWorkflowResponse:
    """
    Update a workflow
    """

    logger.warning(f"Received to update task for id: {dispatch_id}")

    task_execution_results = pickle.loads(task_execution_results)
    task_id = task_execution_results["task_id"]
    del task_execution_results["task_id"]
    task_execution_results["node_id"] = task_id

    updated_result_obj = update_workflow_results(
        task_execution_results=task_execution_results,
        dispatch_id=dispatch_id,
        tasks_queue=workflow_tasks_queue,
    )

    # Empty queue when workflow is no longer running (completed # or failed)
    if updated_result_obj.status != Result.RUNNING and not is_sublattice_dispatch_id(
        updated_result_obj.dispatch_id
    ):

        logger.warning("updated_result_obj status is not RUNNING")

        workflow_status_queue.get()
        workflow_status_queue.put(None)

    update_result_and_ui(updated_result_obj, task_id)

    logger.warning("updated_result_obj status is done")

    return {"response": f"{dispatch_id} workflow updated successfully"}


@router.get("/status", status_code=200)
def get_status():

    if is_empty(workflow_status_queue):
        return {"status": "EMPTY"}

    status = workflow_status_queue.get()
    workflow_status_queue.put(status)

    return {"status": f"{status}"}
