from abc import ABC, abstractmethod


class ClientBase(ABC):

    @property
    @abstractmethod
    def client(self):
        pass

    @property
    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def run(self):
        pass


class ContainerBase(ABC):

    @property
    @abstractmethod
    def id(self):
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
