from pydantic import BaseModel, Field
from fastapi import WebSocket

from oremda.typing import IdType


class ObjectModel(BaseModel):
    id: IdType = Field(...)

    class Config:
        arbitrary_types_allowed = True


class SessionModel(ObjectModel):
    pass


class WebsocketModel(ObjectModel):
    socket: WebSocket = Field(...)
