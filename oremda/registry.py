import json
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from oremda.typing import IOType, JSONType, PortKey, PortInfo, TerminateTaskMessage
from oremda.plasma_client import PlasmaClient
from oremda.clients.base.client import ClientBase as ContainerClient
from oremda.clients.base.container import ContainerBase


class ImageInfo(BaseModel):
    name: str = Field(...)
    inputs: Dict[PortKey, PortInfo] = {}
    outputs: Dict[PortKey, PortInfo] = {}
    params: Dict[str, JSONType] = {}
    container: Optional[ContainerBase] = None

    class Config:
        arbitrary_types_allowed = True


class Registry:
    def __init__(self, memory_client: PlasmaClient, container_client: ContainerClient):
        self.memory_client = memory_client
        self.container_client = container_client
        self.images: Dict[str, ImageInfo] = {}
        self.run_kwargs: Any = {}

    def _inspect(self, image_name: str):
        image: Any = self.container_client.image(image_name)
        return image.labels

    def _info(self, image_name: str):
        info = self.images.get(image_name)
        if info is None:
            labels = self._inspect(image_name)

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
                }
            )
            self.images[image_name] = info

        return info

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
        return info.container is not None

    def run(
        self,
        image_name,
    ):
        info = self._info(image_name)
        container = info.container
        if container is None:
            try:
                container = self.container_client.run(image_name, **self.run_kwargs)
                info.container = container
            except Exception as e:
                print(f"An exception was caught: {e}")
                if container is not None:
                    print("Logs:", container.logs())
                raise

        return container

    def start_containers(self, image_names):
        return [self.run(name) for name in image_names]

    def stop(self, image_name):
        if not self.running(image_name):
            return

        queue_name = self.name(image_name)
        message = json.dumps(TerminateTaskMessage().dict())
        with self.memory_client.open_queue(f"/{queue_name}") as queue:
            queue.send(message)

    def release(self):
        for image_name in self.images:
            self.stop(image_name)
