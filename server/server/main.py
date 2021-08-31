from oremda.display import NoopDisplayHandle
import uuid
import os
import json
import asyncio

from typing import Dict, List, Set
from fastapi import (
    FastAPI,
    Query,
    Body,
    WebSocket,
    WebSocketDisconnect,
    BackgroundTasks,
)
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from oremda.typing import DisplayType, IdType, JSONType, PipelineJSON
from oremda.clients import Client as ContainerClientFactory
from oremda.clients.base import ClientBase as ContainerClient
from oremda.plasma_client import PlasmaClient
from oremda.registry import Registry
from oremda.constants import DEFAULT_OREMDA_VAR_DIR
from oremda.utils.plasma import start_plasma_store
from oremda.typing import ContainerType
from oremda.pipeline import deserialize_pipeline

from .models import (
    SessionModel,
    SerializablePipelineModel,
    PipelineModel,
    WebsocketModel,
)
from .messages import NotificationMessage, pipeline_created
from .observer import ServerPipelineObserver
from .displays import OneDDisplayHandle

app = FastAPI()


# Setup and teardown of the required oremda objects
def lifespan(_app):
    global context

    OREMDA_VAR_DIR = os.environ["OREMDA_VAR_DIR"]
    OREMDA_DATA_DIR = os.environ["OREMDA_DATA_DIR"]
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

        context = GlobalContext(
            **{
                "plasma_client": plasma_client,
                "container_client": container_client,
                "registry": registry,
            }
        )

        yield

    registry.release()


app.router.lifespan_context = lifespan


class GlobalContext(BaseModel):
    plasma_client: PlasmaClient = Field(...)
    container_client: ContainerClient = Field(...)
    registry: Registry = Field(...)
    sessions: Dict[IdType, SessionModel] = {}
    pipelines: Dict[IdType, PipelineModel] = {}
    websockets: Dict[IdType, WebsocketModel] = {}
    session_pipelines: Dict[IdType, Set[IdType]] = {}
    session_websockets: Dict[IdType, Set[IdType]] = {}

    class Config:
        arbitrary_types_allowed = True


context: GlobalContext


async def notify_clients(message: JSONType, session_id: IdType, context: GlobalContext):
    websocket_ids = context.session_websockets.get(session_id, set())
    for websocket_id in websocket_ids:
        websocket = context.websockets[websocket_id]
        await websocket.socket.send_json(message)


async def run_pipeline(session_id: IdType, pipeline_id: IdType, context: GlobalContext):
    pipeline_ids = context.session_pipelines.get(session_id, set())
    if pipeline_id not in pipeline_ids:
        return

    model = context.pipelines[pipeline_id]
    pipeline = model.pipeline

    # pipeline.run is a blocking function, run it in a separate thread to free the
    # server to perform other tasks such as sending notifications
    # TODO: convert pipeline.run to an async function
    await asyncio.to_thread(pipeline.run)


def unique_id():
    return str(uuid.uuid4())


@app.get("/sessions", response_model=List[SessionModel])
async def get_sessions():
    global context

    return list(context.sessions.values())


@app.post("/sessions", response_model=SessionModel)
async def create_session():
    global context

    session_id = unique_id()
    session = SessionModel(id=session_id)
    context.sessions[session_id] = session

    return session


@app.get("/pipelines", response_model=List[SerializablePipelineModel])
async def get_pipelines(session_id: IdType = Query(..., alias="sessionId")):
    global context

    if session_id not in context.sessions:
        raise Exception(f"Session {session_id} does not exist")

    pipeline_ids = context.session_pipelines.get(session_id, set())

    pipelines = list(
        map(lambda pipeline_id: context.pipelines[pipeline_id], pipeline_ids)
    )

    return pipelines


@app.post("/pipelines", response_model=SerializablePipelineModel)
async def create_pipeline(
    background_tasks: BackgroundTasks,
    session_id: IdType = Query(..., alias="sessionId"),
    graph: PipelineJSON = Body(...),
):
    global context

    if session_id not in context.sessions:
        raise Exception(f"Session {session_id} does not exist")

    pipeline_id = unique_id()
    graph.id = pipeline_id

    def notify(message: NotificationMessage):
        asyncio.run(notify_clients(message.dict(), session_id, context))

    def display_factory(id: IdType, display_type: DisplayType):
        if display_type == DisplayType.OneD:
            return OneDDisplayHandle(id, notify)
        else:
            return NoopDisplayHandle(id, display_type)

    pipeline = deserialize_pipeline(
        graph.dict(by_alias=True), context.plasma_client, context.registry, display_factory
    )

    pipeline.observer = ServerPipelineObserver(notify)

    model = PipelineModel(id=pipeline_id, graph=graph, pipeline=pipeline)

    pipeline_ids = context.session_pipelines.setdefault(session_id, set())
    pipeline_ids.add(model.id)

    context.pipelines[model.id] = model

    message = pipeline_created(model)

    background_tasks.add_task(notify_clients, message.dict(), session_id, context)
    background_tasks.add_task(run_pipeline, session_id, model.id, context)

    return model


@app.websocket("/ws")
async def create_websocket(
    socket: WebSocket, session_id: IdType = Query(..., alias="sessionId")
):
    global context

    await socket.accept()

    websocket = WebsocketModel(id=unique_id(), socket=socket)

    websocket_ids = context.session_websockets.setdefault(session_id, set())
    websocket_ids.add(websocket.id)

    context.websockets[websocket.id] = websocket

    try:
        while True:
            _ = await socket.receive_json()
    except WebSocketDisconnect:
        websocket_ids.remove(websocket.id)


@app.get("/")
async def get_index():
    index_file = f"{os.path.join(os.path.dirname(__file__), 'index.html')}"
    with open(index_file) as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/pipeline.json")
async def sample_pipeline():
    pipeline_file = f"{os.path.join(os.path.dirname(__file__), 'pipeline.json')}"
    with open(pipeline_file) as f:
        return json.load(f)
