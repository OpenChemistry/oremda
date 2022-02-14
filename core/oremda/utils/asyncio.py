import asyncio
from functools import partial, wraps
from typing import Callable, Awaitable, Any

from oremda.utils.concurrency import ThreadPoolSingleton


def run_in_executor(f: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    """A decorator to run a function in the asyncio executor

    Uses the default thread pool executor, which can be set via
    loop.set_defaulf_executor().
    """

    @wraps(f)
    def inner(*args: Any, **kwargs: Any) -> Awaitable[Any]:
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, partial(f, *args, **kwargs))

    return inner


def set_executor_to_singleton():
    loop = asyncio.get_running_loop()
    loop.set_default_executor(ThreadPoolSingleton().executor)
