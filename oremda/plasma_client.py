from typing import Optional

import numpy as np
from pydantic import BaseModel, validator
import pyarrow.plasma as plasma


class PlasmaClient:
    def __init__(self, plasma_socket: str):
        self.plasma_client = plasma.connect(plasma_socket)

    def create_object(self, obj: np.ndarray) -> plasma.ObjectID:
        return self.plasma_client.put(obj)

    def get_object(self, object_id: plasma.ObjectID) -> np.ndarray:
        return self.plasma_client.get(object_id)


class PlasmaArray(BaseModel):

    client: PlasmaClient
    object_id: plasma.ObjectID

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, client, object_id, **data):
        super().__init__(client=client, object_id=object_id, **data)

    @validator("object_id", pre=True)
    def validate_object_id(cls, id, values):
        client = values["client"]
        conversions = {
            plasma.ObjectID: lambda x: x,
            str: lambda x: plasma.ObjectID(bytes.fromhex(x)),
            np.ndarray: lambda x: client.create_object(x),
        }

        id_type = type(id)
        if id_type not in conversions:
            raise TypeError(f"Cannot convert type {id_type} to ObjectID")

        return conversions[id_type](id)

    @property
    def hex_id(self):
        return self.object_id.binary().hex()

    @property
    def data(self) -> Optional[np.ndarray]:
        return self.client.get_object(self.object_id)

    @data.setter
    def data(self, array: np.ndarray):
        self.object_id = self.client.create_object(array)
