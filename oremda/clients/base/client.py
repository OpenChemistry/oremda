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
    def image(self, name):
        pass

    @abstractmethod
    def container(self, id):
        pass

    @abstractmethod
    def self_container(self):
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        pass
