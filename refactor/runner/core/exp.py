from multiprocessing import Pool


def task(x):
    return x ** 2


def custom_callback(arg):
    print(f"I'm the callback for {arg}")


def send_node_update_to_dispatcher(dispatch_id, node):
    pass


if __name__ == "__main__":

    pool = Pool(maxtasksperchild=1)

    available_tasks = [
        (task, [6]),
        (task, [5]),
        (task, [4]),
        (task, [3]),
        (task, [2]),
        (task, [1]),
    ]
    available_resources = 4
    execution_results = []

    async_results = []

    # for ar in async_results:
    #     print(ar.get())
    while available_tasks:

        for i in range(available_resources):
            func, args = available_tasks[i]

            async_results.append(pool.apply_async(func, args=args, callback=custom_callback))

            available_resources -= 1
            available_tasks.pop(i)

        i = 0
        while True:
            if i >= len(async_results):
                i = 0

            elif async_results[i].ready():
                available_resources += 1
                break

            i += 1

        send_node_update_to_dispatcher("dispatch_id", async_results[i].get())

        del async_results[i]
