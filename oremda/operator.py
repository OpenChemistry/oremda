from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, Dict, Optional, Tuple

from oremda import PlasmaClient
from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH
from oremda.messengers import MQPMessenger
from oremda.typing import (
    JSONType,
    OperateTaskMessage,
    PortKey,
    DataType,
    MetaType,
    ResultTaskMessage,
    TaskMessage,
    TaskType,
)


class Operator(ABC):
    def __init__(self, name: str, client: PlasmaClient):
        self.name = name
        self.client = client
        self.messenger = MQPMessenger(client)

    @property
    def input_queue_name(self) -> str:
        return f"/{self.name}"

    def start(self):
        while True:
            message = self.messenger.recv(self.input_queue_name)
            task_message = TaskMessage(**message)

            if task_message.task == TaskType.Operate:
                task_message = OperateTaskMessage(**message)
                self.operate(task_message)
            elif task_message.task == TaskType.Terminate:
                return
            else:
                raise Exception(f"Unknown task: {task_message.task}")

    def operate(self, task_message: OperateTaskMessage):
        data_inputs = task_message.data_inputs
        meta_inputs = task_message.meta_inputs
        params = task_message.params
        output_queue_name = task_message.output_queue

        meta_outputs, data_outputs = self.kernel(meta_inputs, data_inputs, params)

        result = ResultTaskMessage(
            **{"meta_outputs": meta_outputs, "data_outputs": data_outputs}
        )
        self.messenger.send(result.dict(), output_queue_name)

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
        self.messenger = MQPMessenger(client)
        self.parameters: JSONType = {}

    def execute(
        self,
        meta_inputs: Dict[PortKey, MetaType],
        data_inputs: Dict[PortKey, DataType],
        output_queue: str,
    ) -> Tuple[Dict[PortKey, MetaType], Dict[PortKey, DataType]]:
        task = OperateTaskMessage(
            **{
                "data_inputs": data_inputs,
                "meta_inputs": meta_inputs,
                "params": self.parameters,
                "output_queue": output_queue,
            }
        )

        self.messenger.send(task.dict(), self.input_queue_name)

        message = self.messenger.recv(output_queue)

        result = ResultTaskMessage(**message)
        return result.meta_outputs, result.data_outputs

    @property
    def input_queue_name(self):
        return f"/{self.name}"
