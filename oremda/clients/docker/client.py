import docker
import os
from typing import List

from oremda.clients.base.client import ClientBase
from oremda.clients.docker.container import DockerContainer
from oremda.clients.docker.image import DockerImage
from oremda import constants


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

    def images(self, organization: str = None) -> List[DockerImage]:
        images = []
        for image in self.client.images.list():
            for tag in image.tags:
                # Apply the organization filter is we have one
                if organization is not None and not tag.startswith(f"{organization}/"):
                    continue

                # Check that we have labels
                docker_image = self.image(tag)
                labels = docker_image.raw_labels

                # Skip over anything without at least a name
                if constants.OREMDA_IMAGE_LABEL_NAME not in labels:
                    continue

                images.append(docker_image)

        return images
