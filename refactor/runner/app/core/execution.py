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


from multiprocessing import Process
from multiprocessing import Queue as MPQ
from typing import Dict, List

from .utils import TaskData


def generate_task_result(task_id, status, output, error, stdout, stderr):
    return {
        "task_id": task_id,
        "status": status,
        "output": output,
        "error": error,
        "stdout": stdout,
        "stderr": stderr,
    }


def send_task_update_to_dispatcher(dispatch_id, task_id, task_result):
    pass


def done_callback_to_runner(dispatch_id, task_id):
    pass


def start_task(task_id, func, args, kwargs, executor, info_queue, dispatch_id):

    # And adding some other stuff if needed to this functions parameters

    task_result = generate_task_result(
        task_id=task_id,
        status="RUNNING",
        output=None,
        error=None,
        stdout=None,
        stderr=None,
    )

    # Set task as running and send update to dispatcher
    send_task_update_to_dispatcher(dispatch_id, task_id, task_result)

    # TODO: Get the correct results back here once we see what
    # the executor is actually returning
    task_output = executor.execute(func, args, kwargs)

    task_result = generate_task_result(
        task_id=task_id,
        status="COMPLETE",
        output=task_output,
        error=None,
        stdout=None,
        stderr=None,
    )

    # No more info needs to be stored about execution
    info_queue.close()

    # Set task as complete and send update to dispatcher
    send_task_update_to_dispatcher(dispatch_id, task_id, task_result)

    # Callback to the runner to close this process and free resources
    done_callback_to_runner(dispatch_id, task_id)


def run_tasks_with_resources(
    dispatch_id: str,
    tasks_left_to_run: List[Dict],
    available_resources: int,
):
    # Example task:
    # {
    #    "task_id": 3,
    #    "func": Callable,
    #    "args": [1, 2, 3],
    #    "kwargs": {"a": 1, "b": 2},
    #    "executor": Executor,
    # }

    tasks_data = {}
    processes = []

    for _ in range(available_resources):

        # Popping first element from tasks_left_to_run
        task = tasks_left_to_run.pop(0)
        info_queue = MPQ()

        # Organizing the args to be sent
        starting_args = (
            task["task_id"],
            task["func"],
            task["args"],
            task["kwargs"],
            task["executor"],
            info_queue,
            dispatch_id,
        )

        process = Process(target=start_task, args=starting_args, daemon=True)
        processes.append(process)

        tasks_data[task["task_id"]] = TaskData(
            process=process, executor=task["executor"], info=info_queue
        )

    # Starting the processes
    for p in processes:
        p.start()

    return tasks_data, tasks_left_to_run


def get_task_status(executor, info_queue):

    info = info_queue.get()
    status = executor.get_status(info)
    info_queue.put(info)

    return status


def cancel_running_task(process, executor, info_queue):

    # Using MPQ to get any information that execute method wanted to
    # share with cancel method
    executor.cancel(info_queue.get())

    # Close the info_queue for any more data transfer
    info_queue.close()
    info_queue.join_thread()

    process.terminate()
    process.join()
