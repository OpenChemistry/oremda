from typing import Any, Dict, Optional, Sequence, Union
from abc import ABC, abstractmethod
from uuid import UUID
import numpy as np
from pydantic import BaseModel, Field
from enum import Enum

IdType = Union[str, UUID]
PortKey = str
ParamKey = str
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
    Operator = "operator"


class PortType(str, Enum):
    Data = "data"
    Meta = "meta"


class IOType(str, Enum):
    In = "in"
    Out = "out"


class ContainerType(str, Enum):
    Docker = "docker"
    Singularity = "singularity"


class PortInfo(BaseModel):
    type: PortType = Field(...)
    name: PortKey = Field(...)
    required: bool = False

    def __eq__(self, other: "PortInfo"):
        return self.type == other.type and self.name == other.name


class MountInfo(BaseModel):
    source: str = Field(...)
    destination: str = Field(...)


class TaskType(str, Enum):
    Operate = "operate"
    Terminate = "terminate"


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
    start: PortJSON = Field(..., alias="from")
    stop: PortJSON = Field(..., alias="to")


class PipelineJSON(BaseModel):
    id: Optional[IdType] = None
    nodes: Sequence[NodeJSON] = []
    edges: Sequence[EdgeJSON] = []


class PortLabels(BaseModel):
    type: PortType = PortType.Data
    required: bool = True


class PortsLabels(BaseModel):
    input: Dict[PortKey, PortLabels] = {}
    output: Dict[PortKey, PortLabels] = {}


class ParamLabels(BaseModel):
    type: str
    required: bool = True


class OperatorLabels(BaseModel):
    name: str
    ports: PortsLabels
    params: Dict[ParamKey, ParamLabels] = {}
