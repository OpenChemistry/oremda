import copy
from typing import Callable, Dict, Union, List

import numpy as np

from oremda.messengers import MQPMessenger
from oremda.plasma_client import PlasmaClient, PlasmaArray
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
        parameters = self.parameters

        if settings.parallel_aware_operator:
            # The operator itself is parallel-aware. Override our settings
            # to allow it to work.
            settings = copy.deepcopy(settings)
            parameters = copy.deepcopy(parameters)

            settings.parallel_param = "parallel_index"
            parameters["parallel_index"] = list(range(settings.num_containers))
            parameters["parallel_world_size"] = settings.num_containers

        self.validate_parallel_param(settings, parameters)

        msg = OperateTaskMessage(
            **{
                "inputs": inputs,
                "output_queue": output_queue,
            }
        )

        task_list = parameters[settings.parallel_param]  # type: ignore
        if settings.distribute_parallel_tasks:
            distributed = distribute_tasks(len(task_list), settings.num_containers)
            task_list = [task_list[start:stop] for start, stop in distributed]

        if settings.parallel_aware_operator:
            # There should only be one task in each. Let's reduce it down.
            task_list = [x[0] for x in task_list]

        # Message queue messengers are non-blocking. Send them all right away.
        for i, task in enumerate(task_list):
            params = copy.deepcopy(parameters)
            params[settings.parallel_param] = task  # type: ignore
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
        output_to_join = settings.parallel_output_to_join

        if output_to_join is not None:
            if any(output_to_join not in x for x in outputs):
                raise Exception(f"{output_to_join} is not in all outputs: {outputs=}")

            # Join methods take a list of arrays to join
            join_methods = {
                "stack": np.hstack,
                "sum": sum,
            }
            method_name = settings.parallel_output_join_method
            if method_name not in join_methods:
                raise NotImplementedError(method_name)

            join = join_methods[method_name]

            # Join.
            join_args = []
            for x in outputs:
                port = x[output_to_join]
                if port.data is not None:
                    join_args.append(port.data.data)

            output[output_to_join] = Port(
                **{
                    "data": PlasmaArray(
                        self.client,
                        join(join_args),
                    ),
                    "meta": outputs[0][output_to_join].meta,
                }
            )

        return output

    @staticmethod
    def validate_parallel_param(settings, parameters):
        if settings.parallel_param is None:
            msg = f"{settings.parallel_param} is not defined, can't run in parallel!"
            raise Exception(msg)

        if settings.parallel_param not in parameters:
            msg = f"{settings.parallel_param} is not in {parameters}!"
            raise Exception(msg)
