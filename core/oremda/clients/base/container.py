from abc import ABC, abstractmethod
from oremda.typing import IdType


class ContainerBase(ABC):
    @property
    @abstractmethod
    def id(self) -> IdType:
        pass

    @abstractmethod
    def logs(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def wait(self):
        pass
