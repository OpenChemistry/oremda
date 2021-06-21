from oremda.constants import NodeType, PortType, IOType

class DataArray:
    def __init__(self, client):
        self.client = client
        self.object_id = None

    @property
    def data(self):
        return self.client.get_object(self.object_id)

    @data.setter
    def data(self, array):
        self.object_id = self.client.create_object(array)

class Source:
    def __init__(self, client):
        self.client = client
        self._data = {}
        self._meta = {}

    def get(self, port):
        if port.type == PortType.Data:
            return self._data[port.name]
            return array.data
        else:
            return self._meta[port.name]
    
    def set(self, port, value):
        key = port.name

        if port.type == PortType.Data:
            if value is None:
                if key in self._data:
                    del self._data[key]
                return

            self._data[key] = value
        else:
            if value is None:
                if key in self._meta:
                    del self._meta[key]
                return

            self._meta[key] = value

    def has(self, port):
        if port.type == PortType.Data:
            return port.name in self._data
        else:
            return port.name in self._meta
