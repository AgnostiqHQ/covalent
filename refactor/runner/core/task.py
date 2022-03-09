from multiprocessing import Queue as MPQ

from .exp import get_task_status, run_available_tasks

cancelled_tasks_queue = MPQ()
track_status_queue = MPQ()
