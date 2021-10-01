from pydantic import BaseModel, Field

from oremda.typing import PipelineJSON, IdType
from oremda.pipeline import Pipeline


class ObjectModel(BaseModel):
    id: IdType = Field(...)

    class Config:
        arbitrary_types_allowed = True


class SerializablePipelineModel(ObjectModel):
    graph: PipelineJSON = Field(...)


class PipelineModel(SerializablePipelineModel):
    pipeline: Pipeline = Field(...)
