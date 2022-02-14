from oremda.clients.base import ImageBase
from oremda.constants import SINGULARITY_FROM_LABEL


class SingularityImage(ImageBase):
    def __init__(self, client, path):
        self.client = client
        self.path = path
        self._name = None

    @property
    def name(self):

        if self._name is None:
            self._name = self.raw_labels.get(SINGULARITY_FROM_LABEL)
            if self._name is None:
                raise Exception("Unable to extract name from Singularity labels.")

        return self._name

    @property
    def raw_labels(self):
        out = self.client.inspect(self.path)
        if "attributes" not in out:
            raise Exception(f"Failed to get attributes: {out}")

        attributes = out["attributes"]
        if "labels" not in attributes:
            raise Exception(f"Failed to get labels: {attributes}")

        return attributes["labels"]
