import docker

from oremda.clients.base import ClientBase
from oremda.clients.docker.container import DockerContainer
from oremda.clients.docker.image import DockerImage


class DockerClient(ClientBase):
    @property
    def client(self):
        return docker.from_env()

    @property
    def type(self):
        return 'docker'

    def image(self, name):
        return DockerImage(self.client, name)

    def run(self, *args, **kwargs):
        # Always run in detached mode
        kwargs = kwargs.copy()
        kwargs['detach'] = True

        container = self.client.containers.run(*args, **kwargs)
        return DockerContainer(container)
