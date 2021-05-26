from abc import ABC, abstractmethod
from functools import wraps
import json

import pyarrow.plasma as plasma

from oremda import Client
from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH, OREMDA_FINISHED_QUEUE


class Operator(ABC):
    def __init__(self, name, client):
        self.name = name
        self.client = client

    def start(self):
        input_queue_name = f'/{self.name}'
        output_queue_name = OREMDA_FINISHED_QUEUE

        with self.client.open_queue(input_queue_name, create=True, reuse=True) as input_queue:
            while True:
                message, priority = input_queue.receive()
                info = json.loads(message)
                object_id = plasma.ObjectID(bytes.fromhex(info.get('object_id')))
                params = info.get('params', {})

                output_object_id = self.execute(object_id, params)

                with self.client.open_queue(output_queue_name) as output_queue:
                    info = {
                        'object_id': output_object_id.binary().hex()
                    }

                    output_queue.send(json.dumps(info))

    def execute(self, object_id, params):
        input_data = self.client.get_object(object_id)

        output_data = self.kernel(input_data, params)

        output_object_id = self.client.create_object(output_data)

        return output_object_id

    @abstractmethod
    def kernel(self, input_data, parameters):
        pass


def operator(func=None, name=None, start=True,
             plasma_socket_path=DEFAULT_PLASMA_SOCKET_PATH):

    # A decorator to automatically make an Operator where the function
    # that is decorated will be the kernel function.

    def decorator(func):
        nonlocal name
        if name is None:
            name = func.__name__

        @wraps(func)
        def kernel(self, *args, **kwargs):
            # Remove self so the caller does not need to add it
            return func(*args, **kwargs)

        OpClass = type(name, (Operator,), {'kernel': kernel})
        obj = OpClass(name, Client(plasma_socket_path))

        if start:
            obj.start()

        return obj

    if func is not None:
        return decorator(func)

    return decorator
