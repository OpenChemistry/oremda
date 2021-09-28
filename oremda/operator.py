from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

from oremda import PlasmaClient
from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH
from oremda.messengers import BaseMessenger, MQPMessenger
from oremda.plasma_client import PlasmaArray
from oremda.typing import (
    JSONType,
    OperateTaskMessage,
    PortKey,
    DataType,
    RawPort,
    ResultTaskMessage,
    MessageType,
    DataArray,
)


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
    name: Optional[str] = None,
    start: bool = True,
    messenger: Optional[BaseMessenger] = None,
    array_constructor: Optional[Callable[[DataType], DataArray]] = None,
) -> Any:
    # A decorator to automatically make an Operator where the function
    # that is decorated will be the kernel function.

    def decorator(func: KernelFn) -> Operator:
        nonlocal name
        nonlocal messenger
        nonlocal array_constructor

        if name is None:
            name = func.__name__

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
