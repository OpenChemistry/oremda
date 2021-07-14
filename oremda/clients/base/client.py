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
