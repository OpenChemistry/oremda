from abc import ABC, abstractmethod
import copy
from functools import wraps
from typing import Callable, Dict, Optional, Union

import numpy as np

from oremda import PlasmaClient
from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH
from oremda.messengers import BaseMessenger, MQPMessenger
from oremda.plasma_client import PlasmaArray
from oremda.typing import (
    JSONType,
    OperateTaskMessage,
    PortKey,
    DataType,
    OperatorConfig,
    Port,
    RawPort,
    ResultTaskMessage,
    MessageType,
    DataArray,
)
from oremda.utils.concurrency import distribute_tasks


class Operator(ABC):
    def __init__(
        self,
        name: str,
        messenger: BaseMessenger,
        array_constructor: Callable[[DataType], DataArray],
    ):
        self.name = name
        self.messenger = messenger
        self.array_constructor = array_constructor

    @property
    def input_queue(self) -> str:
        return f"/{self.name}"

    def start(self):
        while True:
            message = self.messenger.recv(self.input_queue)

            if message.type == MessageType.Operate:
                task_message = OperateTaskMessage(**message.dict())
                self.operate(task_message)
            elif message.type == MessageType.Terminate:
                return
            else:
                raise Exception(f"Unknown message type: {message.type}")

    def operate(self, task_message: OperateTaskMessage):
        inputs = task_message.inputs
        params = task_message.params
        output_queue = task_message.output_queue

        raw_inputs = {key: RawPort.from_port(port) for key, port in inputs.items()}
        _raw_outputs = self.kernel(raw_inputs, params)

        raw_outputs: Dict[PortKey, RawPort] = {
            key: port if isinstance(port, RawPort) else RawPort(**port)
            for key, port in _raw_outputs.items()
        }

        outputs = {
            key: port.to_port(self.array_constructor)
            for key, port in raw_outputs.items()
        }

        result = ResultTaskMessage(outputs=outputs)
        result.parallel_index = task_message.parallel_index
        self.messenger.send(result, output_queue)

    @abstractmethod
    def kernel(
        self,
        inputs: Dict[PortKey, RawPort],
        parameters: JSONType,
    ) -> Union[Dict[PortKey, RawPort], Dict[PortKey, Dict]]:
        pass


KernelFn = Callable[
    [Dict[PortKey, RawPort], JSONType],
    Union[Dict[PortKey, RawPort], Dict[PortKey, Dict]],
]


def operator(
    func: Optional[KernelFn] = None,
    _name: Optional[str] = None,
    start: bool = True,
    messenger: Optional[BaseMessenger] = None,
    array_constructor: Optional[Callable[[DataType], DataArray]] = None,
):
    # A decorator to automatically make an Operator where the function
    # that is decorated will be the kernel function.

    def decorator(func: KernelFn) -> Operator:
        nonlocal _name
        nonlocal messenger
        nonlocal array_constructor

        if _name is None:
            name = func.__name__
        else:
            name = _name

        if messenger is None:
            client = PlasmaClient(DEFAULT_PLASMA_SOCKET_PATH)
            messenger = MQPMessenger(client)

        if array_constructor is None:
            client = PlasmaClient(DEFAULT_PLASMA_SOCKET_PATH)
            array_constructor = lambda data: PlasmaArray(client, data)  # noqa

        @wraps(func)
        def kernel(_, *args, **kwargs):
            # Remove self so the caller does not need to add it
            return func(*args, **kwargs)

        class_name = f"{name.capitalize()}Operator"
        OpClass = type(class_name, (Operator,), {"kernel": kernel})

        obj = OpClass(name, messenger, array_constructor)

        if start:
            obj.start()

        return obj

    if func is not None:
        return decorator(func)

    return decorator


class OperatorHandle:
    def __init__(
        self,
        image_name: str,
        name: str,
        input_queue: str,
        client: PlasmaClient,
        operator_config: OperatorConfig,
    ):
        self.image_name = image_name
        self.name = name
        self.input_queue = input_queue
        self.parameters: JSONType = {}
        self.messenger = MQPMessenger(client)
        self.client = client
        self.operator_config = operator_config

    def execute(
        self,
        inputs: Dict[PortKey, Port],
        output_queue: str,
    ) -> Dict[PortKey, Port]:
        return self.execute_func(inputs, output_queue)

    @property
    def execute_func(self):
        settings = self.operator_config
        return self.execute_parallel if settings.parallel else self.execute_serial

    def execute_serial(self, inputs: Dict[PortKey, Port], output_queue: str):
        task = OperateTaskMessage(
            **{
                "inputs": inputs,
                "params": self.parameters,
                "output_queue": output_queue,
            }
        )

        self.messenger.send(task, self.input_queue)
        message = self.messenger.recv(output_queue)

        if message.type == MessageType.Complete:
            result = ResultTaskMessage(**message.dict())
            return result.outputs
        else:
            raise Exception(f"Unknown message type: {message.type}")

    def execute_parallel(self, inputs: Dict[PortKey, Port], output_queue: str):
        settings = self.operator_config
        if settings.parallel_param not in self.parameters:
            msg = f"{settings.parallel_param} is not in {self.parameters}!"
            raise Exception(msg)

        msg = OperateTaskMessage(
            **{
                "inputs": inputs,
                "output_queue": output_queue,
            }
        )

        task_list = self.parameters[settings.parallel_param]
        if settings.distribute_parallel_tasks:
            distributed = distribute_tasks(len(task_list), settings.num_containers)
            task_list = [task_list[start:stop] for start, stop in distributed]

        # Message queue messengers are non-blocking. Send them all right away.
        for i, task in enumerate(task_list):
            params = copy.deepcopy(self.parameters)
            params[settings.parallel_param] = task
            msg.params = params
            msg.parallel_index = i
            self.messenger.send(msg, self.input_queue)

        # Now receive the outputs
        outputs = [None] * len(task_list)
        for _ in outputs:
            message = self.messenger.recv(output_queue)

            if message.type != MessageType.Complete:
                raise Exception(f"Unknown message type: {message.type}")

            result = ResultTaskMessage(**message.dict())
            i = result.parallel_index
            outputs[i] = result.outputs

        if any(x is None for x in outputs):
            raise Exception(f"Failed to receive some outputs: {outputs=}")

        # Now grab the output parameter to stack
        output_to_stack = settings.parallel_output_to_stack
        if any(output_to_stack not in x for x in outputs):
            raise Exception(f"{output_to_stack} is not in all outputs: {outputs=}")

        # Stack it.
        output = outputs[0]
        output[output_to_stack] = Port(
            **{
                "data": PlasmaArray(
                    self.client,
                    np.hstack([x[output_to_stack].data.data for x in outputs]),
                ),
                "meta": outputs[0][output_to_stack].meta,
            }
        )

        return output
