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

    def unlink(self, source: str):
        # Not every messenger needs to unlink, so the default does nothing.
        # Any messenger that needs to do anything should override this method.
        pass
