import copy
from typing import Callable, Dict, Union, List

import numpy as np

from oremda import PlasmaClient
from oremda.messengers import MQPMessenger
from oremda.plasma_client import PlasmaArray
from oremda.typing import (
    ErrorTaskMessage,
    JSONType,
    OperateTaskMessage,
    PortKey,
    OperatorConfig,
    Port,
    RawPort,
    ResultTaskMessage,
    MessageType,
)
from oremda.utils.concurrency import distribute_tasks


KernelFn = Callable[
    [Dict[PortKey, RawPort], JSONType],
    Union[Dict[PortKey, RawPort], Dict[PortKey, Dict]],
]


class OperatorException(Exception):
    def __init__(self, error_string) -> None:
        self.error_string = error_string


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
        try:
            return self.execute_func(inputs, output_queue)
        finally:
            # Clean up the output queue
            self.messenger.unlink(output_queue)

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
        elif message.type == MessageType.Error:
            error = ErrorTaskMessage(**message.dict())
            raise OperatorException(error.error_string)
        else:
            raise Exception(f"Unknown message type: {message.type}")

    def execute_parallel(self, inputs: Dict[PortKey, Port], output_queue: str):
        settings = self.operator_config

        if settings.parallel_param is None:
            msg = f"{settings.parallel_param} is not defined, can't run in parallel!"
            raise Exception(msg)

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
        outputs: List[Dict[PortKey, Port]] = [{}] * len(task_list)
        for _ in outputs:
            message = self.messenger.recv(output_queue)

            if message.type == MessageType.Error:
                error = ErrorTaskMessage(**message.dict())
                raise OperatorException(error.error_string)
            elif message.type != MessageType.Complete:
                raise Exception(f"Unknown message type: {message.type}")

            result = ResultTaskMessage(**message.dict())
            i = result.parallel_index
            outputs[i] = result.outputs

        if any(x is None for x in outputs):
            raise Exception(f"Failed to receive some outputs: {outputs=}")

        output = outputs[0]

        # Now grab the output parameter to stack
        output_to_stack = settings.parallel_output_to_stack

        if output_to_stack is not None:
            if any(output_to_stack not in x for x in outputs):
                raise Exception(f"{output_to_stack} is not in all outputs: {outputs=}")

            # Stack it.
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
