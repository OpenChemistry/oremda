from oremda.clients.base import ContainerBase


class DockerContainer(ContainerBase):
    def __init__(self, container):
        self.container = container

    @property
    def id(self):
        return self.container.id

    @property
    def status(self):
        return self.container.status

    @property
    def mounts(self):
        return list(
            map(
                lambda mount: {'source': mount['Source'], 'destination': mount['Destination']},
                filter(
                    lambda mount: mount['Type'] == 'bind',
                    self.container.attrs.get('Mounts', [])
                )
            )
        )

    def logs(self, *args, **kwargs):
        return self.container.logs(*args, **kwargs).decode('utf-8')

    def stop(self, *args, **kwargs):
        return self.container.stop(*args, **kwargs)

    def remove(self, *args, **kwargs):
        return self.container.remove(*args, **kwargs)

    def wait(self, *args, **kwargs):
        return self.container.wait(*args, **kwargs)
