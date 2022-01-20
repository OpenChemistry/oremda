from abc import ABC, abstractmethod
from typing import Any, List

from oremda.clients.base.container import ContainerBase
from oremda.clients.base.image import ImageBase
from oremda.constants import OREMDA_MPI_RANK_ENV_VAR
from oremda.typing import ContainerType
from oremda.utils.mpi import mpi_rank


class ClientBase(ABC):
    @property
    @abstractmethod
    def client(self) -> Any:
        pass

    @property
    @abstractmethod
    def type(self) -> ContainerType:
        pass

    @abstractmethod
    def image(self, name: str) -> ImageBase:
        pass

    @abstractmethod
    def run(self, *args, **kwargs) -> ContainerBase:
        pass

    @abstractmethod
    def images(self, organization: str = None) -> List[ImageBase]:
        pass

    def add_mpi_environment_variables(self, kwargs):
        if "environment" not in kwargs:
            kwargs["environment"] = {}

        kwargs["environment"][OREMDA_MPI_RANK_ENV_VAR] = mpi_rank
