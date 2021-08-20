from contextlib import contextmanager

import posix_ipc
from posix_ipc import MessageQueue


@contextmanager
def open_queue(name: str, create=False, consume=False, reuse=False):
    """Open a message queue via a context manager

    The message queue will automatically be closed when the
    context ends. The message queue may also optionally be
    created and/or consumed. If the "consume" flag is True,
    the message queue will be unlinked as well when the context
    ends.

    Args:
        name (str): the name of the message queue
        create (bool): whether to create the message queue or try
                    to open a pre-existing one.
        reuse (bool):  whether to reuse an existing message queue
                       on creation
        consume (bool): whether or not to unlink the message queue
                        when the context ends.

    Yields:
        posix_ipc.MessageQueue: the message queue
    """
    flags = 0
    if create:
        flags = posix_ipc.O_CREAT if reuse else posix_ipc.O_CREX

    queue = None

    if not name.startswith("/"):
        # Message queues requires that the name starts with "/"
        name = f"/{name}"

    try:
        queue = MessageQueue(name, flags=flags)
        yield queue
    finally:
        if queue is not None:
            queue.close()
            if consume:
                queue.unlink()
