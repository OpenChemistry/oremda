import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from oremda.typing import (
    IOType,
    JSONType,
    OperatorConfig,
    PortKey,
    PortInfo,
    TerminateTaskMessage,
)
from oremda.plasma_client import PlasmaClient
from oremda.clients.base.client import ClientBase as ContainerClient
from oremda.clients.base.container import ContainerBase
from oremda.messengers import MQPMessenger
from oremda.utils.mpi import mpi_rank


class ImageInfo(BaseModel):
    name: str = Field(...)
    inputs: Dict[PortKey, PortInfo] = {}
    outputs: Dict[PortKey, PortInfo] = {}
    params: Dict[str, JSONType] = {}
    containers: List[ContainerBase] = []
    running: bool = False
    operator_config: OperatorConfig = OperatorConfig()
    metadata: Optional[Dict[str, JSONType]] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def input_queue(self):
        return f"/{self.name}"


class Registry:
    def __init__(
        self,
        plasma_client: PlasmaClient,
        container_client: ContainerClient,
        operator_config_file: str = None,
    ):
        self.plasma_client = plasma_client
        self.container_client = container_client
        self.operator_config_dict = {}
        self.operator_config_file = operator_config_file
        self.images: Dict[str, ImageInfo] = {}
        self.run_kwargs: Any = {}

    def register(self, image_name: str):
        if image_name in self.images:
            # Already registered
            return

        labels = self._inspect(image_name)

        operator_config = self.operator_config_dict.get(image_name, {})

        info = ImageInfo(
            **{
                "name": labels.name,
                "inputs": {
                    name: PortInfo(**{"name": name, "type": value.type})
                    for name, value in labels.ports.input.items()
                },
                "outputs": {
                    name: PortInfo(**{"name": name, "type": value.type})
                    for name, value in labels.ports.output.items()
                },
                "params": {k: v.dict() for k, v in labels.params.items()},
                "operator_config": OperatorConfig(**operator_config),
            }
        )

        if labels.metadata is not None:
            info.metadata = labels.metadata

        self.images[image_name] = info

    def _inspect(self, image_name: str):
        image: Any = self.container_client.image(image_name)
        return image.labels

    def _info(self, image_name: str) -> ImageInfo:
        return self.images[image_name]

    def name(self, image_name: str):
        info = self._info(image_name)
        return info.name

    def ports(self, image_name: str, io: IOType):
        info = self._info(image_name)
        if io == IOType.In:
            return info.inputs
        else:
            return info.outputs

    def params(self, image_name):
        info = self._info(image_name)
        return info.params

    def running(self, image_name):
        info = self._info(image_name)
        return info.running

    def operator_config(self, image_name):
        info = self._info(image_name)
        return info.operator_config

    def input_queue(self, image_name):
        info = self._info(image_name)
        return info.input_queue

    def run(
        self,
        image_name,
    ):
        info = self._info(image_name)
        if info.running:
            # Already running
            return

        operator_config = info.operator_config
        operator_config.validate_params()
        num_to_run = operator_config.num_containers_on_this_rank

        while len(info.containers) < num_to_run:
            container = None
            try:
                print(f"On {mpi_rank=}, starting {image_name=}")
                container = self.container_client.run(image_name, **self.run_kwargs)
                info.containers.append(container)
            except Exception as e:
                print(f"An exception was caught: {e}")
                if container is not None:
                    print("Logs:", container.logs())
                raise

        info.running = True
        return info.containers

    @property
    def operator_config_file(self):
        return self._operator_config_file

    @operator_config_file.setter
    def operator_config_file(self, v):
        self._operator_config_file = v
        if not v:
            return

        with open(v, "r") as rf:
            self.operator_config_dict = json.load(rf)

    @property
    def image_names(self):
        return list(self.images.keys())

    def start_containers(self):
        return [self.run(name) for name in self.image_names]

    def stop(self, image_name):
        messenger = MQPMessenger(self.plasma_client)
        input_queue = self.input_queue(image_name)
        info = self._info(image_name)

        for _ in range(info.operator_config.num_containers):
            messenger.send(TerminateTaskMessage(), input_queue)

        # Tell it to unlink, so the queue gets removed
        messenger.unlink(input_queue)

        info.running = False

    def release(self):
        for image_name in self.images:
            self.stop(image_name)
