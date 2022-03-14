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
from queue import Empty


def send_node_update_to_dispatcher(dispatch_id, task_id, node_output):
    pass


def start_task(task_id, result_queue, func, args, kwargs, executor):

    # And adding some other stuff if needed to this functions parameters

    result = executor.execute(func, args, kwargs)
    result_queue.put_nowait((task_id, result))


def cancel_task(process):
    process.terminate()
    process.join()
    pass


def new_cancel_task(*args, keyword_only_arg, **kwargs):
    executor = object
    process = object

    # Two options for cancel method of an executor,
    # 1. Executor's cancel method should not take any arguments
    # 2. It does take arguments, this will be more difficult because now
    # we're gonna have to pass arguments from the user straight to this method
    # through http which again will require pickling. One solution that might work
    # is if we limit the types of arguments to be only of jsonify-able type.
    executor.cancel()

    process.terminate()
    process.join()


def update_status_queue(task_id, status, track_status_queue):

    statuses = track_status_queue.get()
    statuses[task_id] = status
    track_status_queue.put(statuses)


def get_task_status(task_id, track_status_queue):

    statuses = track_status_queue.get()
    task_status = statuses[task_id]
    track_status_queue.put(statuses)
    return task_status


def check_task_cancellation(cancelled_queue, track_status_queue, available_tasks, processes):

    try:
        cancelled_task_id = cancelled_queue.get_nowait()
        cancel_task(processes[cancelled_task_id])
        update_status_queue(cancelled_task_id, "CANCELLED", track_status_queue)
        available_tasks.pop(cancelled_task_id)
    except Empty:
        pass

    return available_tasks


def run_available_tasks(
    dispatch_id: str,
    cancelled_queue: MPQ,
    track_status_queue: MPQ,
    available_tasks: list,
    available_resources: int,
):

    processes = {}

    result_queue = MPQ()

    while available_tasks:

        available_tasks = check_task_cancellation(
            cancelled_queue, track_status_queue, available_tasks, processes
        )

        for i in range(available_resources):
            task_id, func, args, kwargs, executor = available_tasks[i]
            starting_args = (task_id, result_queue, func, args, kwargs, executor)

            processes[task_id] = Process(target=start_task, args=starting_args, daemon=True)

            available_tasks.pop(i)
            available_resources -= 1

        for task_id, proc in processes.items():
            proc.start()
            update_status_queue(task_id, "RUNNING", track_status_queue)

        while True:
            try:
                completed_task_id, completed_task_result = result_queue.get_nowait()
                processes[completed_task_id].join()
                del processes[completed_task_id]
                update_status_queue(completed_task_id, "COMPLETED", track_status_queue)

                break
            except Empty:
                available_tasks = check_task_cancellation(
                    cancelled_queue, track_status_queue, available_tasks, processes
                )

        available_resources += 1
        available_tasks += send_node_update_to_dispatcher(
            dispatch_id, completed_task_id, completed_task_result
        )
