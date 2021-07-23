from oremda.typing import IdType, JSONType, PipelineJSON
from typing import Any, Dict, List, Set
from fastapi import FastAPI, Query, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uuid
import os
import json

app = FastAPI()

IdType = str

class ObjectModel(BaseModel):
    id: IdType = Field(...)

class SessionModel(ObjectModel):
    pass

class PipelineModel(ObjectModel):
    graph: PipelineJSON = Field(...)

class WebsocketModel(ObjectModel):
    socket: WebSocket = Field(...)

    class Config:
        arbitrary_types_allowed = True

class GlobalContext(BaseModel):
    sessions: Dict[IdType, SessionModel] = {}
    pipelines: Dict[IdType, PipelineModel] = {}
    websockets: Dict[IdType, WebsocketModel] = {}
    session_pipelines: Dict[IdType, Set[IdType]] = {}
    session_websockets: Dict[IdType, Set[IdType]] = {}

context = GlobalContext()

async def notify_clients(message: JSONType, session_id: IdType, context: GlobalContext):
    websocket_ids = context.session_websockets.get(session_id, set())
    for websocket_id in websocket_ids:
        websocket = context.websockets[websocket_id]
        await websocket.socket.send_json(message)

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

@app.get("/pipelines", response_model=List[PipelineModel])
async def get_pipelines(
    session_id: IdType = Query(..., alias='sessionId')
):
    global context

    if session_id not in context.sessions:
        raise Exception(f"Session {session_id} does not exist")

    pipeline_ids = context.session_pipelines.get(session_id, set())

    pipelines = list(map(lambda pipeline_id: context.pipelines[pipeline_id], pipeline_ids))

    return pipelines


@app.post("/pipelines", response_model=PipelineModel)
async def create_pipeline(
    session_id: IdType = Query(..., alias='sessionId'),
    graph: PipelineJSON = Body(...)
):
    global context

    if session_id not in context.sessions:
        raise Exception(f"Session {session_id} does not exist")

    pipeline = PipelineModel(id=unique_id(), graph=graph)

    pipeline_ids = context.session_pipelines.setdefault(session_id, set())
    pipeline_ids.add(pipeline.id)

    context.pipelines[pipeline.id] = pipeline

    message = {
        'type': '@@OREMDA',
        'action': 'PIPELINE_CREATED',
        'payload': pipeline.dict()
    }
    await notify_clients(message, session_id, context)

    return pipeline

@app.websocket("/ws")
async def create_websocket(
    socket: WebSocket,
    session_id: IdType = Query(..., alias='sessionId')
):
    global context

    await socket.accept()

    websocket = WebsocketModel(id=unique_id(), socket=socket)

    websocket_ids = context.session_websockets.setdefault(session_id, set())
    websocket_ids.add(websocket.id)

    context.websockets[websocket.id] = websocket

    try:
        while True:
            data = await socket.receive()
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
