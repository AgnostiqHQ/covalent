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


import traceback
from datetime import datetime, timezone
from multiprocessing import Process
from multiprocessing import Queue as MPQ
from typing import Dict, List

import cloudpickle as pickle
import requests
from app.core.get_svc_uri import DispatcherURI, RunnerURI

from covalent._results_manager.result import Result

from .runner_logger import logger


def generate_task_result(
    task_id,
    start_time=None,
    end_time=None,
    status=None,
    output=None,
    error=None,
    stdout=None,
    stderr=None,
    info=None,
):

    return {
        "task_id": task_id,
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "output": output,
        "error": error,
        "stdout": stdout,
        "stderr": stderr,
        "info": info,
    }


def send_task_update_to_dispatcher(dispatch_id, task_result):

    url = DispatcherURI().get_route(f"workflow/{dispatch_id}")
    response = requests.put(url=url, files={"task_execution_results": pickle.dumps(task_result)})
    response.raise_for_status()

    logger.warning(f"{dispatch_id}")
    logger.warning(f"{task_result}")


def free_resources_call_to_runner(dispatch_id, task_id):

    url = RunnerURI().get_route(f"workflow/{dispatch_id}/task/{task_id}/free")
    response = requests.post(url=url)
    response.raise_for_status()


def done_callback_to_runner(dispatch_id, task_id):

    url = RunnerURI().get_route(f"workflow/{dispatch_id}/task/{task_id}/done")
    response = requests.post(url=url)
    response.raise_for_status()


def start_task(task_id, func, args, kwargs, executor, results_dir, info_queue, dispatch_id):

    # These objects were pickled (with cloudpickle) in run_tasks_with_resources so as to be
    # compatible (pickleable) with multiprocessing processes.
    args = pickle.loads(args)
    kwargs = pickle.loads(kwargs)
    executor = pickle.loads(executor)

    task_result = generate_task_result(
        task_id=task_id,
        start_time=datetime.now(timezone.utc),
        status=Result.RUNNING,
    )

    # Set task as running and send update to dispatcher
    send_task_update_to_dispatcher(dispatch_id, task_result)

    logger.warning(f"info queue when inside the process {info_queue}")

    task_output, stdout, stderr, exception = executor.execute(
        function=func,
        args=args,
        kwargs=kwargs,
        info_queue=info_queue,
        task_id=task_id,
        dispatch_id=dispatch_id,
        results_dir=results_dir,
    )

    task_result = generate_task_result(
        task_id=task_id,
        end_time=datetime.now(timezone.utc),
        status=Result.FAILED if exception else Result.COMPLETED,
        output=task_output,
        error="".join(traceback.TracebackException.from_exception(exception).format())
        if exception
        else None,
        stdout=stdout,
        stderr=stderr,
        info=info_queue.get(),
    )

    # No more info needs to be stored about execution
    info_queue.close()

    # Free resources callback to runner
    free_resources_call_to_runner(dispatch_id, task_id)

    # Set task as complete and send update to dispatcher
    send_task_update_to_dispatcher(dispatch_id, task_result)

    # Callback to the runner to close this process
    done_callback_to_runner(dispatch_id, task_id)


def run_tasks_with_resources(
    dispatch_id: str,
    tasks_left_to_run: List[Dict],
    resources: MPQ,
    ultimate_dict: dict,
):
    # Example task:
    # {
    #    "task_id": 3,
    #    "func": Callable,
    #    "args": [1, 2, 3],
    #    "kwargs": {"a": 1, "b": 2},
    #    "executor": Executor,
    #    "results_dir": "/path/to/results/"
    # }

    if not ultimate_dict.get(dispatch_id):
        ultimate_dict[dispatch_id] = {}

    # Get number of available resources
    available_resources = resources.get()
    resources.put(available_resources)

    while available_resources > 0 and tasks_left_to_run:

        # Reduce the number of available resources
        resources.put(resources.get() - 1)

        # Popping first element from tasks_left_to_run
        task = tasks_left_to_run.pop(0)
        info_queue = MPQ()

        logger.warning(f"info queue when starting the process {info_queue}")

        # Organizing the args to be sent
        starting_args = (
            task["task_id"],
            task["func"],
            pickle.dumps(task["args"]),
            pickle.dumps(task["kwargs"]),
            pickle.dumps(task["executor"]),
            task["results_dir"],
            info_queue,
            dispatch_id,
        )

        process = Process(target=start_task, args=starting_args, daemon=True)
        process.start()

        ultimate_dict[dispatch_id][task["task_id"]] = {
            "process": process,
            "executor": pickle.dumps(task["executor"]),
            "info_queue": info_queue,
        }

        available_resources = resources.get()
        resources.put(available_resources)

    return tasks_left_to_run


def get_task_status(executor, info_queue):

    info = info_queue.get()
    status = executor.get_status(info)
    info_queue.put(info)

    return status


def cancel_running_task(executor, info_queue):

    # Using MPQ to get any information that execute method wanted to
    # share with cancel method
    executor.cancel(info_queue.get())

    # Close the info_queue for any more data transfer
    info_queue.close()
    info_queue.join_thread()
