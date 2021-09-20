from contextlib import contextmanager

from typing import Dict, Set

from pydantic import BaseModel, Field

from oremda.typing import IdType
from oremda.clients import Client as ContainerClientFactory
from oremda.clients.base import ClientBase as ContainerClient
from oremda.plasma_client import PlasmaClient
from oremda.registry import Registry
from oremda.constants import DEFAULT_OREMDA_VAR_DIR
from oremda.utils.plasma import start_plasma_store
from oremda.typing import ContainerType
from oremda.pipeline.runner.config import settings

from oremda.models import (
    SessionModel,
    WebsocketModel,
)

from oremda.pipeline.models import (
    PipelineModel,
)


class SessionWebModel(BaseModel):
    session: SessionModel
    pipelines: Set[IdType] = set()
    websockets: Set[IdType] = set()


class GlobalContext(BaseModel):
    plasma_client: PlasmaClient = Field(...)
    container_client: ContainerClient = Field(...)
    registry: Registry = Field(...)
    sessions: Dict[IdType, SessionWebModel] = {}
    pipelines: Dict[IdType, PipelineModel] = {}
    websockets: Dict[IdType, WebsocketModel] = {}

    class Config:
        arbitrary_types_allowed = True


@contextmanager
def pipeline_context():
    OREMDA_VAR_DIR = settings.OREMDA_VAR_DIR
    OREMDA_DATA_DIR = settings.OREMDA_DATA_DIR
    PLASMA_SOCKET = f"{OREMDA_VAR_DIR}/plasma.sock"

    plasma_kwargs = {"memory": 50_000_000, "socket_path": PLASMA_SOCKET}

    with start_plasma_store(**plasma_kwargs):
        plasma_client = PlasmaClient(PLASMA_SOCKET)
        container_client = ContainerClientFactory(ContainerType.Docker)
        registry = Registry(plasma_client, container_client)

        registry.run_kwargs = {
            "volumes": {
                OREMDA_VAR_DIR: {"bind": DEFAULT_OREMDA_VAR_DIR},
                OREMDA_DATA_DIR: {"bind": "/data"},
            },
            "ipc_mode": "host",
            "detach": True,
            "working_dir": "/data",
        }

        yield GlobalContext(
            **{
                "plasma_client": plasma_client,
                "container_client": container_client,
                "registry": registry,
            }
        )

    registry.release()
