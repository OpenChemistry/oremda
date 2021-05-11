from contextlib import contextmanager
from multiprocessing.shared_memory import SharedMemory

import posix_ipc
from posix_ipc import MessageQueue


@contextmanager
def open_queue(name, create=False, consume=False):
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
        consume (bool): whether or not to unlink the message queue
                        when the context ends.

    Yields:
        posix_ipc.MessageQueue: the message queue
    """
    flags = 0
    if create:
        flags = posix_ipc.O_CREX

    queue = MessageQueue(name, flags=flags)
    try:
        yield queue
    finally:
        queue.close()
        if consume:
            queue.unlink()


@contextmanager
def open_memory(name, create=False, size=0, consume=False):
    """Open shared memory via a context manager

    The shared memory will automatically be closed when the
    context ends. The shared memory may also optionally be
    created and/or consumed. If the "consume" flag is True,
    the shared memory will be unlinked as well when the context
    ends.

    Args:
        name (str): the name of the shared memory
        create (bool): whether to create the shared memory or try
                       to open a pre-existing one. If this is True,
                       the size argument must be non-zero.
        size (int): the size in bytes of the shared memory block to create.
                    Only used if create == True.
        consume (bool): whether or not to unlink the shared memory
                        when the context ends.

    Yields:
        posix_ipc.MessageQueue: the message queue
    """
    if create and size == 0:
        raise Exception('If create is True, size must be non-zero')

    kwargs = {
        'name': name,
        'create': create,
        'size': size,
    }
    shm = SharedMemory(**kwargs)
    try:
        yield shm
    finally:
        shm.close()
        if consume:
            shm.unlink()
