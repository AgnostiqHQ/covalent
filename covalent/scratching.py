import time
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool


def f(x):
    print(f"Start {x}")
    y = 0
    for i in range(int(1e6)):
        y += i
    print(f"Stop {x}")


def f_1(x):
    print(f"Start {x}")
    time.sleep(1)
    print(f"Stop {x}")


if __name__ == "__main__":
    start_time = time.time()
    # p = ThreadPool()
    p = Pool()

    for i in range(100):
        p.apply_async(f, args=(i,))

    p.close()
    p.join()

    print(f"Time taken: {time.time() - start_time}")
