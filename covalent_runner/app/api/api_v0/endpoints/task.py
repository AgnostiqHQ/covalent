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


import sys
from datetime import datetime, timezone
from multiprocessing import Queue as MPQ

import cloudpickle as pickle
from app.core.execution import (
    cancel_running_task,
    generate_task_result,
    get_task_status,
    run_tasks_with_resources,
    send_task_update_to_dispatcher,
)
from app.core.runner_logger import logger
from app.schemas.task import CancelResponse, RunTaskResponse, TaskPickleList, TaskStatus
from fastapi import APIRouter, File

from covalent._results_manager.result import Result

INITAL_AVAILABLE_RESOURCES = 1

print(f"INITIAL_AVAILABLE_RESOURCES: {INITAL_AVAILABLE_RESOURCES}")

resources = MPQ()
resources.put(INITAL_AVAILABLE_RESOURCES)


router = APIRouter()

# Sample:
# example_ultimate_data = {

#     "dispatch_id_1": {
#         "task_id_1": TaskData(None, None, None),
#         "task_id_2": TaskData(None, None, None),
#     },

#     "dispatch_id_2": {
#         "task_id_1": TaskData(None, None, None),
#         "task_id_2": TaskData(None, None, None),
#     }

# }

ultimate_dict = {}

logger.warning("Runner Service Started")


@router.post("/{dispatch_id}/tasks", status_code=202, response_model=RunTaskResponse)
async def run_tasks(*, dispatch_id: str, tasks: bytes = File(...)) -> RunTaskResponse:
    """
    Run a list of tasks

    Note: The request body contains a list of "string"s which are pickled objects (bytes) containing
    the following info about the Task:

    `task_id`: Task ID \n
    `func`: Callable function which will be run \n
    `args`: Positional arguments for `func` \n
    `kwargs`: Keyword arguments for `func` \n
    `executor`: Executor object (https://covalent.readthedocs.io/en/latest/api/api.html#local-executor)\n

    Example: \n

    ```
    def task_func_1(x, y):
        return x * y

    def task_func_2(a):
        return a ** 2

    executor_1 = LocalExecutor() \n
    executor_2 = LocalExecutor()

    task_1 = pickle.dumps({"task_id": 0, "func": task_func_1, "args": (1, 2), "kwargs": {}, "executor": executor_1}) \n
    task_2 = pickle.dumps({"task_id": 1, "func": task_func_2, "args": (3,), "kwargs": {}, "executor": executor_2})

    requests.post(f'localhost:48008/api/workflow/{dispatch_id}/tasks', body=pickle.dumps([task_1, task_2]))
    ```
    """

    logger.warning(f"POST on /{dispatch_id}/tasks called to submit a list of tasks")

    runnable_tasks = pickle.loads(tasks)

    logger.warning(f"ultimate dict before {ultimate_dict}")

    tasks_left_to_run = run_tasks_with_resources(
        dispatch_id, runnable_tasks, resources, ultimate_dict
    )

    logger.warning(f"ultimate dict after {ultimate_dict}")

    # Returning the task ids which were not run due to insufficient resources
    left_out_task_ids = [task["task_id"] for task in tasks_left_to_run]

    return {"left_out_task_ids": left_out_task_ids}


@router.get("/{dispatch_id}/task/{task_id}", status_code=200, response_model=TaskStatus)
async def check_status(*, dispatch_id: str, task_id: int) -> TaskStatus:
    """
    Check status of a task
    """

    logger.warning(f"GET on /{dispatch_id}/task/{task_id} called to check status")

    # Pass in the executor and info_queue to get status from the executor
    task_status = get_task_status(
        pickle.loads(ultimate_dict[dispatch_id][task_id]["executor"]),
        ultimate_dict[dispatch_id][task_id]["info_queue"],
    )

    return {"status": f"{task_status}"}


@router.delete("/{dispatch_id}/task/{task_id}", status_code=200, response_model=CancelResponse)
async def cancel_task(*, dispatch_id: str, task_id: int) -> CancelResponse:
    """
    Cancel a task
    """

    print(f"DELETE on /{dispatch_id}/task/{task_id} called to cancel task", file=sys.stderr)

    # print(
    #     f"ultimate dict in cancel before cancelling {[(k, list(v)[0]) for k, v in ultimate_dict.items()]}",
    #     file=sys.stderr,
    # )

    # Cancel a task by calling its executor's cancel method and closing the info_queue
    cancel_running_task(
        executor=pickle.loads(ultimate_dict[dispatch_id][task_id]["executor"]),
        info_queue=ultimate_dict[dispatch_id][task_id]["info_queue"],
    )

    # Free the resources
    free_resources(dispatch_id=dispatch_id, task_id=task_id)

    # Terminate the process
    task_done(dispatch_id=dispatch_id, task_id=task_id)

    # Send updated task result to dispatcher
    task_result = generate_task_result(
        task_id=task_id,
        end_time=datetime.now(timezone.utc),
        status=Result.CANCELLED,
    )

    # ultimate_dict = {
    #     "dispatch_id": {"task_id": {"sdasf":12, "sfsdf": fdsf}}
    # }

    # print(
    #     f"ultimate dict in cancel after cancelling {[(k, list(v)[0]) for k, v in ultimate_dict.items()]}",
    #     file=sys.stderr,
    # )

    send_task_update_to_dispatcher(dispatch_id=dispatch_id, task_result=task_result)

    return {"cancelled_dispatch_id": f"{dispatch_id}", "cancelled_task_id": f"{task_id}"}


@router.post("/{dispatch_id}/task/{task_id}/free", status_code=200)
def free_resources(*, dispatch_id: str, task_id: int) -> None:
    """
    Callback to the runner to free resources
    """

    logger.warning(f"POST on /{dispatch_id}/task/{task_id}/free called to free resources")

    resources.put(resources.get() + 1)

    logger.warning("FREEING RESOURCES DONE")


@router.post("/{dispatch_id}/task/{task_id}/done", status_code=200)
def task_done(*, dispatch_id: str, task_id: int) -> None:
    """
    Callback to the runner to join the process
    """

    logger.warning(
        f"POST on /{dispatch_id}/task/{task_id}/done called to terminate and join the process"
    )

    ultimate_dict[dispatch_id][task_id]["process"].terminate()
    ultimate_dict[dispatch_id][task_id]["process"].join()

    del ultimate_dict[dispatch_id][task_id]

    if not ultimate_dict.get(dispatch_id):
        del ultimate_dict[dispatch_id]
