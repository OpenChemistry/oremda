from oremda.clients.base import ImageBase


class SingularityImage(ImageBase):
    def __init__(self, client, path):
        self.client = client
        self.path = path

    @property
    def raw_labels(self):
        out = self.client.inspect(self.path)
        if "attributes" not in out:
            raise Exception(f"Failed to get attributes: {out}")

        attributes = out["attributes"]
        if "labels" not in attributes:
            raise Exception(f"Failed to get labels: {attributes}")

        return attributes["labels"]
