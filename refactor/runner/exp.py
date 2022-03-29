import logging
from multiprocessing import Process, Queue


def execute(qq):
    res = "X" * 10
    logging.warning(f"queue inside execute function {qq}")
    qq.put(res)


def start_task(q):
    logging.warning(f"queue inside start_task function {q}")
    execute(q)


if __name__ == "__main__":
    queue = Queue()
    logging.warning(f"queue inside main function {queue}")
    p = Process(target=start_task, args=(queue,))
    print(queue.get())
    p.start()
    p.join()
