from abc import ABC, abstractmethod
from oremda.clients.base.container import ContainerBase
from oremda.clients.base.image import ImageBase
from oremda.typing import ContainerType
from typing import Any


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
