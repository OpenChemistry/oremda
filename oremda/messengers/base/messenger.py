from abc import ABC, abstractmethod

from oremda.typing import Message

class BaseMessenger(ABC):
    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @abstractmethod
    def send(self, msg: Message, dest: str):
        pass

    @abstractmethod
    def recv(self, source: str) -> Message:
        pass
