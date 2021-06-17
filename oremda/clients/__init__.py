from oremda.clients.odocker import DockerClient
from oremda.clients.singularity import SingularityClient


container_types = {
    'docker': DockerClient,
    'singularity': SingularityClient,
}


def Client(type='docker'):
    if type not in container_types:
        raise Exception(f'Unknown container type: {type}')

    return container_types[type]()
