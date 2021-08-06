from abc import ABC, abstractmethod
from typing import Sequence
from oremda.typing import IdType, MountInfo


class ContainerBase(ABC):
    @property
    @abstractmethod
    def id(self) -> IdType:
        pass

    @property
    @abstractmethod
    def mounts(self) -> Sequence[MountInfo]:
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
