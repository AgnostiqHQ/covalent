import asyncio
from multiprocessing import Pool

import uvloop


def task(x):
    return x ** 2


def custom_callback(arg):
    print(f"I'm the callback for {arg}")


if __name__ == "__main__":

    pool = Pool(maxtasksperchild=1)

    args = [[5], [4], [3]]

    async_results = [pool.apply_async(task, args=arg, callback=custom_callback) for arg in args]

    i = 0
    while True:
        if i >= len(async_results):
            i = 0

        elif async_results[i].ready():
            break

        i += 1
