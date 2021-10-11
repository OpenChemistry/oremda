from typing import Any, Callable, Dict, Optional, Sequence, Union
from abc import ABC, abstractmethod
from uuid import UUID
import numpy as np
from pydantic import BaseModel, Field, Extra
from enum import Enum

from oremda.utils.mpi import mpi_rank, mpi_world_size

IdType = Union[str, UUID]
PortKey = str
ParamKey = str
JSONType = Dict[str, Any]
DataType = np.ndarray
MetaType = JSONType


# Plasma's ObjectID doesn't have proper typings (cython?),
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
    Display = "display"


class PortType(str, Enum):
    Data = "data"
    Display = "display"


class IOType(str, Enum):
    In = "in"
    Out = "out"


class DisplayType(str, Enum):
    OneD = "1D"
    TwoD = "2D"
    ThreeD = "3D"


class PlotType1D(str, Enum):
    Line = "line"
    Scatter = "scatter"
    Histograms = "histograms"


class PlotType2D(str, Enum):
    Image = "image"
    Points = "points"
    Vectors = "vectors"


class NormalizeType(str, Enum):
    Linear = "linear"
    Log = "log"


class ContainerType(str, Enum):
    Docker = "docker"
    Singularity = "singularity"


class LocationType(str, Enum):
    Local = "local"
    Remote = "remote"


class DataArray(ABC):
    @property
    @abstractmethod
    def data(self) -> DataType:
        pass

    @data.setter
    @abstractmethod
    def data(self, data: DataType):
        pass


class Port(BaseModel):
    meta: Optional[MetaType] = None
    data: Optional[DataArray] = None

    class Config:
        arbitrary_types_allowed = True


class RawPort(BaseModel):
    meta: Optional[MetaType] = None
    data: Optional[DataType] = None

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_port(cls, port: Port):
        raw_port = cls()

        if port.meta is not None:
            raw_port.meta = port.meta

        if port.data is not None:
            raw_port.data = port.data.data

        return raw_port

    def to_port(self, array_factory: Callable[[DataType], DataArray]):
        port = Port()

        if self.meta is not None:
            port.meta = self.meta

        if self.data is not None:
            array = array_factory(self.data)
            port.data = array

        return port


class PortInfo(BaseModel):
    type: PortType = Field(...)
    name: PortKey = Field(...)
    required: bool = False

    def __eq__(self, other: "PortInfo"):
        return self.type == other.type and self.name == other.name


class MountInfo(BaseModel):
    source: str = Field(...)
    destination: str = Field(...)


class MessageType(str, Enum):
    Operate = "operate"
    Terminate = "terminate"
    Complete = "complete"
    MPINodeReady = "mpi_node_ready"
    Error = "error"


class Message(BaseModel):
    type: MessageType

    class Config:
        extra = Extra.allow


class OperateTaskMessage(Message):
    class Config:
        arbitrary_types_allowed = True

    type = MessageType.Operate
    inputs: Dict[PortKey, Port] = {}
    params: JSONType = {}
    output_queue: str
    parallel_index: int = 0


class ResultTaskMessage(Message):
    class Config:
        arbitrary_types_allowed = True

    type = MessageType.Complete
    outputs: Dict[PortKey, Port] = {}
    parallel_index: int = 0


class ErrorTaskMessage(Message):
    type = MessageType.Error
    error_string: str
    parallel_index: int = 0


class TerminateTaskMessage(Message):
    type = MessageType.Terminate


class MPINodeReadyMessage(Message):
    type = MessageType.MPINodeReady
    queue: Optional[str] = None


class PortJSON(BaseModel):
    id: IdType
    port: PortKey


class NodeJSON(BaseModel):
    id: IdType
    type: NodeType = NodeType.Operator
    params: JSONType = {}

    class Config:
        extra = Extra.allow


class OperatorNodeJSON(NodeJSON):
    image: str
    location: str = LocationType.Local


class DisplayNodeJSON(NodeJSON):
    display: DisplayType


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
    description: Optional[str]
    ports: PortsLabels
    params: Dict[ParamKey, ParamLabels] = {}


class OperatorConfig(BaseModel):
    run_locations: Sequence[int] = [0]
    parallel: bool = False
    distribute_parallel_tasks: bool = True
    parallel_param: Optional[str] = None
    parallel_output_to_stack: Optional[str] = None

    @property
    def num_containers(self):
        return len(self.run_locations)

    @property
    def num_containers_on_this_rank(self):
        return self.run_locations.count(mpi_rank)

    def validate_params(self):
        if not all(0 <= x < mpi_world_size for x in self.run_locations):
            msg = (
                f"All run locations ({self.run_locations}) must "
                f"be between 0 and {mpi_world_size=}"
            )
            raise Exception(msg)

        if self.parallel:
            if not self.parallel_param or not self.parallel_output_to_stack:
                msg = (
                    "If parallel is True, then parallel_param and "
                    "parallel_output_to_stack are required!"
                )
                raise Exception(msg)
