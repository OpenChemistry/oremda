from enum import Enum
from oremda.typing import JSONType
from pydantic import BaseModel
from pydantic.fields import Field

from ..models import ObjectModel, PipelineModel, SerializablePipelineModel

OREMDA_TOKEN = '@@OREMDA'

class ActionType(str, Enum):
    PipelineCreated = 'PIPELINE_CREATED'
    PipelineUpdated = 'PIPELINE_UPDATED'
    PipelineStarted = 'PIPELINE_STARTED'
    PipelineCompleted = 'PIPELINE_COMPLETED'

class NotificationMessage(BaseModel):
    type = OREMDA_TOKEN
    action: ActionType = Field(...)
    payload: JSONType

def pipeline_created(pipeline: PipelineModel):
    return NotificationMessage(**{
        'action': ActionType.PipelineCreated,
        'payload': SerializablePipelineModel(**pipeline.dict(by_alias=True))
    })

def pipeline_started(pipeline: PipelineModel):
    return NotificationMessage(**{
        'action': ActionType.PipelineStarted,
        'payload': ObjectModel(**pipeline.dict())
    })

def pipeline_completed(pipeline: PipelineModel):
    return NotificationMessage(**{
        'action': ActionType.PipelineCompleted,
        'payload': ObjectModel(**pipeline.dict())
    })
