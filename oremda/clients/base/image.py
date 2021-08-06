from abc import ABC, abstractmethod

from pydantic.error_wrappers import ValidationError

from oremda.clients.utils import flat_get_item, flat_to_nested
from oremda.typing import OperatorLabels


class ImageBase(ABC):
    @property
    @abstractmethod
    def raw_labels(self):
        pass

    @property
    def labels(self) -> OperatorLabels:
        labels = flat_get_item(self.raw_labels, "oremda")
        return OperatorLabels(**flat_to_nested(labels))

    def validate_labels(self):
        try:
            self.labels
        except ValidationError as e:
            msg = f"Required labels are missing under the oremda prefix:\n{e}"
            raise Exception(msg) from None
