from contextlib import contextmanager
from typing import Optional

from oremda.typing import DataType, ObjectId

import posix_ipc
from posix_ipc import MessageQueue

import pyarrow.plasma as plasma
import numpy as np


class Client:
    def __init__(self, plasma_socket: str):
        self.plasma_client = plasma.connect(plasma_socket)

    def create_object(self, obj: DataType):
        object_id: ObjectId = self.plasma_client.put(obj)

        return object_id

    def get_object(self, object_id: ObjectId) -> DataType:
        return self.plasma_client.get(object_id)

    @contextmanager
    def open_queue(self, name: str, create=False, consume=False, reuse=False):
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

        try:
            queue = MessageQueue(name, flags=flags)
            yield queue
        finally:
            if queue is not None:
                queue.close()
                if consume:
                    queue.unlink()

class DataArray:
    def __init__(self, client: Client):
        self.client = client
        self.object_id: Optional[ObjectId] = None

    @property
    def data(self) -> Optional[DataType]:
        if self.object_id is None:
            return None

        self.client.get_object(self.object_id)

    @data.setter
    def data(self, array: DataType):
        self.object_id = self.client.create_object(array)
