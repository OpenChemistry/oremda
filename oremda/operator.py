from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, Dict, Optional, Tuple
import json

import pyarrow.plasma as plasma

from oremda import DataArray, PlasmaClient
from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH
from oremda.typing import (
    JSONType,
    OperateTaskMessage,
    PortKey,
    DataType,
    MetaType,
    ResultTaskMessage,
    TaskMessage,
    TaskType,
    ObjectId,
)


class Operator(ABC):
    def __init__(self, name: str, client: PlasmaClient):
        self.name = name
        self.client = client

    @property
    def input_queue_name(self) -> str:
        return f"/{self.name}"

    def start(self):
        with self.client.open_queue(
            self.input_queue_name, create=True, reuse=True, consume=True
        ) as input_queue:
            while True:
                message, priority = input_queue.receive()
                message = json.loads(message)

                task_message = TaskMessage(**message)

                if task_message.task == TaskType.Operate:
                    task_message = OperateTaskMessage(**message)
                    self.operate(task_message)
                elif task_message.task == TaskType.Terminate:
                    return
                else:
                    raise Exception(f"Unknown task: {task_message.task}")

    def operate(self, task_message: OperateTaskMessage):
        _data_inputs = task_message.data_inputs
        meta_inputs = task_message.meta_inputs
        params = task_message.params
        output_queue_name = task_message.output_queue

        data_inputs: Dict[PortKey, ObjectId] = {}
        for key, object_id in _data_inputs.items():
            data_inputs[key] = plasma.ObjectID(bytes.fromhex(object_id))

        meta_outputs, data_outputs = self.execute(meta_inputs, data_inputs, params)

        _data_outputs = {}
        for key, object_id in data_outputs.items():
            _data_outputs[key] = object_id.binary().hex()

        with self.client.open_queue(output_queue_name) as output_queue:
            result = ResultTaskMessage(
                **{"meta_outputs": meta_outputs, "data_outputs": _data_outputs}
            )

            output_queue.send(json.dumps(result.dict()))

    def execute(
        self,
        meta_inputs: Dict[PortKey, MetaType],
        data_inputs_id: Dict[PortKey, ObjectId],
        params: JSONType,
    ) -> Tuple[Dict[PortKey, MetaType], Dict[PortKey, plasma.ObjectID]]:
        data_inputs: Dict[PortKey, DataType] = {}
        for key, object_id in data_inputs_id.items():
            data_inputs[key] = self.client.get_object(object_id)

        meta_outputs, data_outputs = self.kernel(meta_inputs, data_inputs, params)

        data_outputs_id: Dict[PortKey, ObjectId] = {}
        for key, array in data_outputs.items():
            data_outputs_id[key] = self.client.create_object(array)

        return meta_outputs, data_outputs_id

    @abstractmethod
    def kernel(
        self,
        meta: Dict[PortKey, MetaType],
        data: Dict[PortKey, DataType],
        parameters: JSONType,
    ) -> Tuple[Dict[PortKey, MetaType], Dict[PortKey, DataType]]:
        pass


KernelFn = Callable[
    [Dict[PortKey, MetaType], Dict[PortKey, DataType], JSONType],
    Tuple[Dict[PortKey, MetaType], Dict[PortKey, DataType]],
]


def operator(
    func: Optional[KernelFn] = None,
    _name: Optional[str] = None,
    start: bool = True,
    plasma_socket_path: str = DEFAULT_PLASMA_SOCKET_PATH,
):

    # A decorator to automatically make an Operator where the function
    # that is decorated will be the kernel function.

    def decorator(func: KernelFn) -> Operator:
        nonlocal _name

        if _name is None:
            name = func.__name__
        else:
            name = _name

        @wraps(func)
        def kernel(_, *args, **kwargs):
            # Remove self so the caller does not need to add it
            return func(*args, **kwargs)

        class_name = f"{name.capitalize()}Operator"
        OpClass = type(class_name, (Operator,), {"kernel": kernel})
        obj = OpClass(name, PlasmaClient(plasma_socket_path))

        if start:
            obj.start()

        return obj

    if func is not None:
        return decorator(func)

    return decorator


class OperatorHandle:
    def __init__(self, image_name: str, name: str, client: PlasmaClient):
        self.image_name = image_name
        self.name = name
        self.client = client
        self._parameters: JSONType = {}

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, params: JSONType):
        self._parameters = params

    def execute(
        self,
        meta_inputs: Dict[PortKey, MetaType],
        data_inputs: Dict[PortKey, DataArray],
        output_queue: str,
    ) -> Tuple[Dict[PortKey, MetaType], Dict[PortKey, DataArray]]:
        data_inputs_id: Dict[PortKey, str] = {}

        for key, arr in data_inputs.items():
            if arr.object_id is None:
                raise Exception(
                    "Trying to perform operator on un-initialized DataArray"
                )

            data_inputs_id[key] = arr.object_id.binary().hex()

        task = OperateTaskMessage(
            **{
                "data_inputs": data_inputs_id,
                "meta_inputs": meta_inputs,
                "params": self.parameters,
                "output_queue": output_queue,
            }
        )

        with self.client.open_queue(
            self.input_queue_name, create=True, reuse=True
        ) as op_queue:
            op_queue.send(json.dumps(task.dict()))

        with self.client.open_queue(
            output_queue,
            create=True,
            reuse=True,
            consume=True,
        ) as done_queue:
            message, priority = done_queue.receive()
            message = json.loads(message)

            result = ResultTaskMessage(**message)

            meta_outputs = result.meta_outputs
            data_outputs_id = result.data_outputs

            data_outputs: Dict[PortKey, DataArray] = {}
            for key, object_id in data_outputs_id.items():
                data_outputs[key] = DataArray(self.client, object_id)

            return meta_outputs, data_outputs

    @property
    def input_queue_name(self):
        return f"/{self.name}"
