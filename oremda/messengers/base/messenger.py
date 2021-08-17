from abc import ABC, abstractmethod


class BaseMessenger(ABC):
    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @abstractmethod
    def send(self, msg: dict, dest: str):
        pass

    @abstractmethod
    def recv(self, source: str) -> dict:
        pass
