import docker

from oremda.clients.base import ClientBase, ContainerBase


class DockerClient(ClientBase):
    @property
    def client(self):
        return docker.from_env()

    @property
    def type(self):
        return 'docker'

    def run(self, *args, **kwargs):
        # Always run in detached mode
        kwargs = kwargs.copy()
        kwargs['detach'] = True

        container = self.client.containers.run(*args, **kwargs)
        return DockerContainer(container)


class DockerContainer(ContainerBase):
    def __init__(self, container):
        self.container = container

    @property
    def id(self):
        return self.container.id

    @property
    def status(self):
        return self.container.status

    def logs(self, *args, **kwargs):
        return self.container.logs(*args, **kwargs).decode('utf-8')

    def stop(self, *args, **kwargs):
        return self.container.stop(*args, **kwargs)

    def remove(self, *args, **kwargs):
        return self.container.remove(*args, **kwargs)

    def wait(self, *args, **kwargs):
        return self.container.wait(*args, **kwargs)
