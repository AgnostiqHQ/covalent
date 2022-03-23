from multiprocessing import Process, Queue


def om(e):
    return e


def f(q):
    res = om("X" * 10)
    q.put(res)


if __name__ == "__main__":
    queue = Queue()
    p = Process(target=f, args=(queue,))
    p.start()
    p.join()  # this deadlocks
    print(queue.get())
