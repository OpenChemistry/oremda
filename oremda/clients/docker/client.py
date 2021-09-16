import docker
import os

from oremda.clients.base.client import ClientBase
from oremda.clients.docker.container import DockerContainer
from oremda.clients.docker.image import DockerImage


class DockerClient(ClientBase):
    @property
    def client(self):
        return docker.from_env()  # type: ignore

    @property
    def type(self):
        return "docker"

    def image(self, name):
        return DockerImage(self.client, name)

    def container(self, id):
        return DockerContainer(self.client.containers.get(id))

    def self_container(self):
        try:
            return self.container(os.environ.get("HOSTNAME"))
        except Exception:
            return None

    def run(self, *args, **kwargs):
        # Always run in detached mode
        kwargs = kwargs.copy()
        kwargs["detach"] = True

        container = self.client.containers.run(*args, **kwargs)
        return DockerContainer(container)
