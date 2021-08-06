from pathlib import Path

from spython.main import Client as client

from oremda.clients.base.client import ClientBase
from oremda.clients.singularity.container import SingularityContainer
from oremda.clients.singularity.image import SingularityImage


class SingularityClient(ClientBase):
    @property
    def client(self):
        return client

    @property
    def type(self):
        return "singularity"

    def image(self, path):
        return SingularityImage(self.client, path)

    def run(self, image, *args, **kwargs):
        kwargs = self._docker_kwargs_to_singularity(kwargs)

        name = Path(image).stem
        container = SingularityContainer(image, name)
        container.run(*args, **kwargs)

        return container

    def _docker_kwargs_to_singularity(self, kwargs):
        # This converts docker-style kwargs to singularity
        ret = {}
        options = []
        if kwargs.get("detach", False) is False:
            msg = "Detach mode is currently required for singularity"
            raise Exception(msg)

        if "ipc_mode" in kwargs:
            print("Warning: IPC mode will be ignored for singularity")

        if "volumes" in kwargs:
            volumes = kwargs["volumes"]
            for key, val in volumes.items():
                bind = val["bind"]
                options += ["--bind", f"{key}:{bind}"]

        ret["options"] = options
        return ret
