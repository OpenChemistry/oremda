from contextlib import contextmanager
from multiprocessing.shared_memory import SharedMemory

import posix_ipc
from posix_ipc import MessageQueue

import pyarrow.plasma as plasma
import numpy as np


class Client(object):
    def __init__(self, plasma_socket):
        self.plasma_client = plasma.connect(plasma_socket)

    def create_object(self, obj):
        object_id = self.plasma_client.put(obj)

        return object_id

    def get_object(self, object_id):
        return self.plasma_client.get(object_id)

    @contextmanager
    def open_queue(self, name, create=False, consume=False, reuse=False):
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
            flags = posix_ipc.O_CREX

        queue = None

        try:
            queue = MessageQueue(name, flags=flags)
            yield queue
        except posix_ipc.ExistentialError:
            if reuse:
                queue = MessageQueue(name, flags=0)
                yield queue
            else:
                raise
        finally:
            if queue is not None:
                queue.close()
                if consume:
                    queue.unlink()
