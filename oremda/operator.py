from abc import ABC, abstractmethod
from functools import wraps
from oremda.plasma_client import PlasmaArray
from typing import Callable, Dict, Optional, Union

from oremda import PlasmaClient
from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH
from oremda.messengers import BaseMessenger, MQPMessenger
from oremda.typing import (
    JSONType,
    OperateTaskMessage,
    PortKey,
    DataType,
    LocationType,
    Port,
    RawPort,
    ResultTaskMessage,
    MessageType,
    DataArray,
)
from oremda.utils.mpi import mpi_rank


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
    def location(self):
        if mpi_rank == 0:
            return LocationType.Local

        return LocationType.Remote

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
        messenger: BaseMessenger,
        location: LocationType,
    ):
        self.image_name = image_name
        self.name = name
        self.input_queue = input_queue
        self.parameters: JSONType = {}
        self.messenger = messenger
        self.location = location

    def execute(
        self,
        inputs: Dict[PortKey, Port],
        output_queue: str,
    ) -> Dict[PortKey, Port]:
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
