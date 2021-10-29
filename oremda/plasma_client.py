from oremda.typing import DataType, ObjectId, DataArray
from typing import Any, Union, get_args

import pyarrow.plasma as plasma


class PlasmaClient:
    def __init__(self, plasma_socket: str):
        self.plasma_client = plasma.connect(plasma_socket)

    def create_object(self, obj: DataType) -> plasma.ObjectID:
        return self.plasma_client.put(obj)

    def get_object(self, object_id: plasma.ObjectID) -> DataType:
        return self.plasma_client.get(object_id)


class PlasmaArray(DataArray):
    def __init__(
        self, client: PlasmaClient, id_or_data: Union[str, plasma.ObjectID, DataType]
    ):
        self.client = client
        self.object_id: ObjectId
        if isinstance(id_or_data, plasma.ObjectID):
            object_id: Any = id_or_data
            self.object_id = object_id
        elif isinstance(id_or_data, str):
            self.object_id = plasma.ObjectID(bytes.fromhex(id_or_data))
        # Note: We have to use get_args as isinstance(...) will not work
        # directly we a Union type.
        elif isinstance(id_or_data, get_args(DataType)):
            self.object_id = self.client.create_object(id_or_data)
        else:
            raise TypeError("Cannot initialize data array.")

    @property
    def hex_id(self) -> str:
        return self.object_id.binary().hex()

    @property
    def data(self) -> DataType:
        return self.client.get_object(self.object_id)

    @data.setter
    def data(self, data: DataType):
        self.object_id = self.client.create_object(data)
