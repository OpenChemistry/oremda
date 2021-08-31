from abc import ABC, abstractmethod
from typing import Callable
from oremda.typing import DisplayType, IdType, JSONType, Port


class DisplayHandle(ABC):
    def __init__(self, id: IdType, type: DisplayType):
        self.id = id
        self._type = type
        self._parameters: JSONType = {}

    @abstractmethod
    def add(self, sourceId: IdType, input: Port):
        pass

    @abstractmethod
    def remove(self, sourceId: IdType):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def render(self):
        pass

    @property
    def type(self) -> DisplayType:
        return self._type

    @property
    def parameters(self) -> JSONType:
        return self._parameters

    @parameters.setter
    def parameters(self, parameters: JSONType):
        self._parameters = parameters

DisplayFactory = Callable[[IdType, DisplayType], DisplayHandle]

class NoopDisplayHandle(DisplayHandle):
    def add(self, sourceId: IdType, input: Port):
        pass

    def remove(self, sourceId: IdType):
        pass

    def render(self):
        pass

    def clear(self):
        pass
