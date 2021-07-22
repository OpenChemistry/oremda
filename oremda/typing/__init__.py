from typing import Any, Dict, NewType, Optional, Sequence, Type, Union
from abc import ABC, abstractmethod
from uuid import UUID
import numpy as np
from pydantic import BaseModel, Field
from enum import Enum

IdType = Union[str, UUID]
PortKey = str
JSONType = Dict[str, Any]
DataType = np.ndarray
MetaType = JSONType

# Plasma's ObjectID doesn't have propert typings (cython?),
# manually create a partial interface for it
class ObjectId(ABC):
    @abstractmethod
    def __init__(self, binary: Optional[bytes]):
        pass

    @abstractmethod
    def binary(self) -> bytes:
        pass

class NodeType(str, Enum):
    Operator = 'operator'

class PortType(str, Enum):
    Data = 'data'
    Meta = 'meta'

class IOType(str, Enum):
    In = 'in'
    Out = 'out'

class TaskType(str, Enum):
    Operate = 'operate'
    Terminate = 'terminate'

class TaskMessage(BaseModel):
    task: TaskType

class OperateTaskMessage(TaskMessage):
    task = TaskType.Operate
    data_inputs: Dict[PortKey, str] = {}
    meta_inputs: Dict[PortKey, MetaType] = {}
    params: JSONType = {}

class ResultTaskMessage(BaseModel):
    data_outputs: Dict[PortKey, str] = {}
    meta_outputs: Dict[PortKey, MetaType] = {}

class TerminateTaskMessage(TaskMessage):
    task = TaskType.Terminate

class PortJSON(BaseModel):
    id: IdType
    port: PortKey

class NodeJSON(BaseModel):
    id: IdType
    image: str
    params: JSONType

class EdgeJSON(BaseModel):
    type: PortType = Field(...)
    start: PortJSON = Field(..., alias='from')
    stop: PortJSON = Field(..., alias='to')

class PipelineJSON(BaseModel):
    nodes: Sequence[NodeJSON] = []
    edges: Sequence[EdgeJSON] = []
