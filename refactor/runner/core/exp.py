from multiprocessing import Pool


def task(x):
    return x ** 2


def custom_callback(arg):
    print(f"I'm the callback for {arg}")


def send_node_update_to_dispatcher(dispatch_id, task_id, node_output):
    pass


def wait_task_complete(async_results, available_resources):

    i = 0
    while True:
        if i >= len(async_results):
            i = 0

        elif async_results[i].ready():
            available_resources += 1
            break

        i += 1

    return i, available_resources


if __name__ == "__main__":

    pool = Pool(maxtasksperchild=1)

    task_ids = [0, 1, 2, 3, 4, 5, 6]

    available_tasks = [
        (task_ids[0], task, [6]),
        (task_ids[1], task, [5]),
        (task_ids[2], task, [4]),
        (task_ids[3], task, [3]),
        (task_ids[4], task, [2]),
        (task_ids[5], task, [1]),
    ]
    available_resources = 4
    execution_results = []

    async_results = []

    while available_tasks:

        for task_index in range(available_resources):
            task_id, func, args = available_tasks[task_index]

            async_results.append(pool.apply_async(func, args=args, callback=custom_callback))

            available_resources -= 1
            available_tasks.pop(task_index)

        completed_task_index, available_resources = wait_task_complete(
            async_results, available_resources
        )

        # async_results[completed_task_index].get() will also return the task id
        available_tasks += send_node_update_to_dispatcher(
            "dispatch_id", async_results[completed_task_index].get()
        )

        del async_results[completed_task_index]
