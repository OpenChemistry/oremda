from abc import ABC, abstractmethod
from functools import wraps
import json

import pyarrow.plasma as plasma

from oremda import Client, DataArray
from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH, OREMDA_FINISHED_QUEUE, TaskType


class Operator(ABC):
    def __init__(self, name, client):
        self.name = name
        self.client = client

    @property
    def input_queue_name(self):
        return f'/{self.name}'

    @property
    def output_queue_name(self):
        return OREMDA_FINISHED_QUEUE

    def start(self):
        with self.client.open_queue(self.input_queue_name, create=True,
                                    reuse=True, consume=True) as input_queue:
            while True:
                message, priority = input_queue.receive()
                info = json.loads(message)

                task = info.get('task', 'operate')

                if task == TaskType.Terminate:
                    return
                elif task == TaskType.Operate:
                    self.operate(info)
                else:
                    raise Exception(f'Unknown task: {task}')
    
    def operate(self, info):
        _data_inputs = info.get('data_inputs', {})
        meta_inputs = info.get('meta_inputs', {})
        params = info.get('params', {})

        data_inputs = {}
        for key, object_id in _data_inputs.items():
            data_inputs[key] = plasma.ObjectID(bytes.fromhex(object_id))

        meta_outputs, data_outputs = self.execute(meta_inputs, data_inputs, params)

        _data_outputs = {}
        for key, object_id in data_outputs.items():
            _data_outputs[key] = object_id.binary().hex()

        with self.client.open_queue(self.output_queue_name) as output_queue:
            info = {
                'meta_outputs': meta_outputs,
                'data_outputs': _data_outputs
            }

            output_queue.send(json.dumps(info))

    def execute(self, meta_inputs, data_inputs_id, params):
        data_inputs = {}
        for key, object_id in data_inputs_id.items():
            data_inputs[key] = self.client.get_object(object_id)

        meta_outputs, data_outputs = self.kernel(meta_inputs, data_inputs, params)

        data_outputs_id = {}
        for key, array in data_outputs.items():
            data_outputs_id[key] = self.client.create_object(array)

        return meta_outputs, data_outputs_id

    @abstractmethod
    def kernel(self, meta, data, parameters):
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

        class_name = f'{name.capitalize()}Operator'
        OpClass = type(class_name, (Operator,), {'kernel': kernel})
        obj = OpClass(name, Client(plasma_socket_path))

        if start:
            obj.start()

        return obj

    if func is not None:
        return decorator(func)

    return decorator

class OperatorHandle:
    def __init__(self, name, client):
        self.name = name
        self.client = client
        self._parameters = {}
    
    @property
    def parameters(self):
        return self._parameters
    
    @parameters.setter
    def parameters(self, params):
        self._parameters = params

    def execute(self, meta_inputs, data_inputs):
        data_inputs_id = {}

        for key, arr in data_inputs.items():
            data_inputs_id[key] = arr.object_id.binary().hex()
        
        info = {
            'task': TaskType.Operate,
            'data_inputs': data_inputs_id,
            'meta_inputs': meta_inputs,
            'params': self.parameters
        }

        with self.client.open_queue(self.queue_name, create=True, reuse=True) as op_queue:
            op_queue.send(json.dumps(info))

        with self.client.open_queue(OREMDA_FINISHED_QUEUE, create=True, reuse=True) as done_queue:
            message, priority = done_queue.receive()

            info = json.loads(message)

            meta_outputs = info.get('meta_outputs', {})
            data_outputs_id = info.get('data_outputs', {})

            data_outputs = {}
            for key, object_id in data_outputs_id.items():
                arr = DataArray(self.client)
                arr.object_id = plasma.ObjectID(bytes.fromhex(object_id))
                data_outputs[key] = arr

            return meta_outputs, data_outputs

    @property
    def queue_name(self):
        return f'/{self.name}'
