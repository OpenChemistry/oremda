from typing import Union

from oremda.clients.base.client import ClientBase
from oremda.clients.docker import DockerClient
from oremda.clients.singularity import SingularityClient
from oremda.typing import ContainerType


container_types = {
    ContainerType.Docker: DockerClient,
    ContainerType.Singularity: SingularityClient,
}


def Client(type: Union[ContainerType, str] = ContainerType.Docker) -> ClientBase:
    type = ContainerType(type)
    if type not in container_types:
        raise Exception(f'Unknown container type: {type}')

    return container_types[type]()
