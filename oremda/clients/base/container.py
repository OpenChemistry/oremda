from abc import ABC, abstractmethod


class ContainerBase(ABC):

    @property
    @abstractmethod
    def id(self):
        pass

    @property
    @abstractmethod
    def mounts(self):
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
