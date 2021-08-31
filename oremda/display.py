from abc import ABC, abstractmethod
from oremda.typing import DataType, IdType, MetaType

class DisplayHandle(ABC):
    @abstractmethod
    def draw(self, id: IdType, meta: MetaType, data: DataType):
        pass

    @abstractmethod
    def remove(self, id: IdType):
        pass
