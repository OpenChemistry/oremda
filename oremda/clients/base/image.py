from abc import ABC, abstractmethod

from oremda.clients.utils import flat_get_item, flat_to_nested


class ImageBase(ABC):

    @property
    @abstractmethod
    def labels(self):
        pass

    @property
    def oremda_labels(self):
        oremda_labels = flat_get_item(self.labels, 'oremda')
        return flat_to_nested(oremda_labels)
