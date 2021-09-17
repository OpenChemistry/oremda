from typing import Dict, Set
from pydantic import BaseModel

from oremda.typing import IdType

from oremda.models import SessionModel
from oremda.pipeline.models import (
    PipelineModel,
)

from oremda.models import (
    WebsocketModel,
)


class GlobalContext(BaseModel):
    sessions: Dict[IdType, SessionModel] = {}
    pipelines: Dict[IdType, PipelineModel] = {}
    websockets: Dict[IdType, WebsocketModel] = {}
    session_pipelines: Dict[IdType, Set[IdType]] = {}
    session_websockets: Dict[IdType, Set[IdType]] = {}

    class Config:
        arbitrary_types_allowed = True


context: GlobalContext = GlobalContext()
