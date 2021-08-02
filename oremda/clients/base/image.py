from abc import ABC, abstractmethod

from oremda.clients.utils import flat_get_item, flat_to_nested


class ImageBase(ABC):

    @property
    @abstractmethod
    def raw_labels(self):
        pass

    @property
    def labels(self):
        labels = flat_get_item(self.raw_labels, 'oremda')
        return flat_to_nested(labels)
