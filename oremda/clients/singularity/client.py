from functools import wraps
from pathlib import Path
import re

from spython.main import Client as client

from oremda.clients.base.client import ClientBase
from oremda.clients.singularity.container import SingularityContainer
from oremda.clients.singularity.image import SingularityImage


def with_resolved_path(func):
    @wraps(func)
    def wrapped(self, path, *args, **kwargs):
        path = self.resolve_path(path)
        return func(self, path, *args, **kwargs)

    return wrapped


class SingularityClient(ClientBase):
    def __init__(self):
        super().__init__()

        self.images_dir = ""

    @property
    def client(self):
        return client

    @property
    def type(self):
        return "singularity"

    @with_resolved_path
    def image(self, path):
        return SingularityImage(self.client, path)

    @with_resolved_path
    def run(self, path, *args, **kwargs):
        kwargs = self._docker_kwargs_to_singularity(kwargs)

        name = Path(path).stem
        container = SingularityContainer(path, name)
        container.run(*args, **kwargs)

        return container

    @staticmethod
    def docker_name_to_singularity(name):
        return re.sub("[:/]", "_", f"{name}.sif")

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

        if "working_dir" in kwargs:
            options += ["--pwd", kwargs["working_dir"]]

        ret["options"] = options
        return ret

    def resolve_path(self, path):
        full_path = self.images_dir / Path(path)
        paths_tried = [full_path]
        if full_path.exists():
            # If it exists, then assume it is already a path...
            return str(full_path)

        # Otherwise, it may be a docker image name.
        # Use regex to convert it to a valid singularity name.
        name = self.docker_name_to_singularity(path)
        full_path = self.images_dir / Path(name)
        paths_tried += [full_path]
        if full_path.exists():
            return str(full_path)

        msg = f"Cannot resolve singularity image path for {path}"
        if self.images_dir:
            msg += f" with images directory: {self.images_dir}"

        msg += ".\nTried:\n"
        for p in paths_tried:
            msg += f"  {p}\n"
        raise Exception(msg)
