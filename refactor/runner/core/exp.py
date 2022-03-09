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
