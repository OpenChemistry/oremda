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
