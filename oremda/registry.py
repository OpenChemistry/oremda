from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from oremda.typing import (
    IOType,
    JSONType,
    LocationType,
    PortKey,
    PortInfo,
    TerminateTaskMessage,
)
from oremda.plasma_client import PlasmaClient
from oremda.clients.base.client import ClientBase as ContainerClient
from oremda.clients.base.container import ContainerBase
from oremda.messengers import Messenger
from oremda.utils.mpi import mpi_rank


class ImageInfo(BaseModel):
    name: str = Field(...)
    inputs: Dict[PortKey, PortInfo] = {}
    outputs: Dict[PortKey, PortInfo] = {}
    params: Dict[str, JSONType] = {}
    container: Optional[ContainerBase] = None
    running: bool = False
    location: LocationType = LocationType.Local
    node: int = 0

    class Config:
        arbitrary_types_allowed = True

    @property
    def input_queue(self):
        funcs = {
            LocationType.Local: lambda: f"/{self.name}",
            LocationType.Remote: lambda: self.node,
        }
        return funcs[self.location]()


class Registry:
    def __init__(self, plasma_client: PlasmaClient, container_client: ContainerClient):
        self.plasma_client = plasma_client
        self.container_client = container_client
        self.images: Dict[str, ImageInfo] = {}
        self.num_remote = 0
        self.run_kwargs: Any = {}

    def register(self, image_name: str, location: LocationType):
        if image_name in self.images:
            # Already registered
            # Make sure the location matches so there are no surprises...
            if self.images[image_name].location != location:
                orig_loc = self.images[image_name].location
                msg = (
                    f"For '{image_name}', location '{location}' does not "
                    f"match previous location: '{orig_loc}'"
                )
                raise Exception(msg)

            return

        labels = self._inspect(image_name)

        if location == LocationType.Remote:
            self.num_remote += 1
            node = self.num_remote
            running = True
        else:
            node = 0
            running = False

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
                "location": location,
                "node": node,
                "running": running,
            }
        )
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

    def location(self, image_name):
        info = self._info(image_name)
        return info.location

    def node(self, image_name):
        info = self._info(image_name)
        return info.node

    def input_queue(self, image_name):
        info = self._info(image_name)
        return info.input_queue

    @property
    def image_for_rank(self):
        for key, info in self.images.items():
            if info.node == mpi_rank:
                return key

    def run_image_for_rank(self):
        return self.run(self.image_for_rank)

    def run(
        self,
        image_name,
    ):
        info = self._info(image_name)
        if info.node != mpi_rank:
            # This container is not for this node
            return

        container = info.container
        if container is None:
            try:
                container = self.container_client.run(image_name, **self.run_kwargs)
                info.container = container
                info.running = True
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

        location = self.location(image_name)
        messenger = Messenger(location, self.plasma_client)
        input_queue = self.input_queue(image_name)
        messenger.send(TerminateTaskMessage(), input_queue)

        self._info(image_name).running = False

    def release(self):
        for image_name in self.images:
            self.stop(image_name)
