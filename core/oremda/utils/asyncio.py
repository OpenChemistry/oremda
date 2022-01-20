import asyncio
from functools import partial, wraps

from oremda.utils.concurrency import ThreadPoolSingleton


def run_in_executor(f):
    """A decorator to run a function in the asyncio executor

    Uses the default thread pool executor, which can be set via
    loop.set_defaulf_executor().
    """

    @wraps(f)
    def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, partial(f, *args, **kwargs))

    return inner


def set_executor_to_singleton():
    loop = asyncio.get_running_loop()
    loop.set_default_executor(ThreadPoolSingleton().executor)
