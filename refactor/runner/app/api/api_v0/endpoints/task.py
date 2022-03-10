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


from app.schemas.task import CancelResponse, RunTaskResponse, TaskPickleList, TaskStatus
from fastapi import APIRouter

router = APIRouter()


@router.post("/{dispatch_id}/tasks", status_code=202, response_model=RunTaskResponse)
def run_tasks(*, dispatch_id: str, tasks: TaskPickleList) -> RunTaskResponse:
    """
    Run a list of tasks

    Note: The request body contains a list of "string"s which are pickled objects (bytes) containing
    the following info about the Task:

    `id`: Task ID \n
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

    task_1 = pickle.dumps({"id": 0, "func": task_func_1, "args": (1, 2), "kwargs": {}, "executor": executor_1}) \n
    task_2 = pickle.dumps({"id": 1, "func": task_func_2, "args": (3,), "kwargs": {}, "executor": executor_2})

    requests.post(f'localhost:48008/api/workflow/{dispatch_id}/tasks', body=pickle.dumps([task_1, task_2]))
    ```
    """

    return {"response": "execution of tasks started"}


@router.get("/{dispatch_id}/task/{task_id}", status_code=200, response_model=TaskStatus)
def check_status(*, dispatch_id: str, task_id: int) -> TaskStatus:
    """
    Check status of a task
    """

    return {"status": "running"}


@router.delete("/{dispatch_id}/task/{task_id}", status_code=200, response_model=CancelResponse)
def cancel_task(*, dispatch_id: str, task_id: int) -> CancelResponse:
    """
    Cancel a task
    """

    return {"cancelled_dispatch_id": f"{dispatch_id}", "cancelled_task_id": f"{task_id}"}
