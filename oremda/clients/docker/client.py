import docker
import os

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

    def container(self, id):
        return DockerContainer(self.client.containers.get(id))

    def self_container(self):
        return self.container(os.environ.get('HOSTNAME'))

    def run(self, *args, **kwargs):
        # Always run in detached mode
        kwargs = kwargs.copy()
        kwargs['detach'] = True

        container = self.client.containers.run(*args, **kwargs)
        return DockerContainer(container)
