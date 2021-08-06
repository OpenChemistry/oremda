from pydantic import BaseModel, Field
from fastapi import WebSocket

from oremda.typing import PipelineJSON
from oremda.pipeline import Pipeline

from ..typing import IdType


class ObjectModel(BaseModel):
    id: IdType = Field(...)

    class Config:
        arbitrary_types_allowed = True


class SessionModel(ObjectModel):
    pass


class SerializablePipelineModel(ObjectModel):
    graph: PipelineJSON = Field(...)


class PipelineModel(SerializablePipelineModel):
    pipeline: Pipeline = Field(...)


class WebsocketModel(ObjectModel):
    socket: WebSocket = Field(...)
