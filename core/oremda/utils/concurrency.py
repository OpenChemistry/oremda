from concurrent.futures import ThreadPoolExecutor
import os

from oremda.utils.singleton import Singleton


class ThreadPoolSingleton(Singleton):
    """A singleton with a ThreadPoolExecutor

    This can be used throughout the program in places that use threads
    in order to re-use threads and limit the number of threads that
    get launched.
    """

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=os.cpu_count())
        self.submit = self.executor.submit


def distribute_tasks(num_tasks, max_workers=os.cpu_count()):
    # Distribute tasks as evenly as possible to each worker.
    # Returns a list of tuples, where each tuple in the list
    # represents the [start, stop) task range for a worker.
    result = []
    num_assigned = 0

    tasks_per_worker = num_tasks // max_workers
    remainder = num_tasks % max_workers
    for i in range(max_workers):
        if num_assigned == num_tasks:
            break

        tasks = tasks_per_worker
        if remainder != 0:
            tasks += 1
            remainder -= 1

        if i == 0:
            previous = 0
        else:
            previous = result[-1][1]

        result.append((previous, previous + tasks))
        num_assigned += tasks

    return result
