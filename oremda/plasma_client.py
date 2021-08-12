from contextlib import contextmanager
from pydantic import BaseModel, validator
from typing import Optional

from oremda.typing import DataType

import posix_ipc
from posix_ipc import MessageQueue

import pyarrow.plasma as plasma


class PlasmaClient:
    def __init__(self, plasma_socket: str):
        self.plasma_client = plasma.connect(plasma_socket)

    def create_object(self, obj: DataType) -> plasma.ObjectID:
        return self.plasma_client.put(obj)

    def get_object(self, object_id: plasma.ObjectID) -> DataType:
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


class PlasmaArray(BaseModel):

    client: PlasmaClient
    object_id: plasma.ObjectID

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, client, object_id, **data):
        super().__init__(client=client, object_id=object_id, **data)

    @validator("object_id", pre=True)
    def validate_object_id(cls, id, values):
        client = values["client"]
        conversions = {
            plasma.ObjectID: lambda x: x,
            str: lambda x: plasma.ObjectID(bytes.fromhex(x)),
            DataType: lambda x: client.create_object(x),
        }

        id_type = type(id)
        if id_type not in conversions:
            raise TypeError(f"Cannot convert type {id_type} to ObjectID")

        return conversions[id_type](id)

    @property
    def hex_id(self):
        return self.object_id.binary().hex()

    @property
    def data(self) -> Optional[DataType]:
        self.client.get_object(self.object_id)

    @data.setter
    def data(self, array: DataType):
        self.object_id = self.client.create_object(array)
