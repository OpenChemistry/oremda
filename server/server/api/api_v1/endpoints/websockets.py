from fastapi import Query, WebSocket, WebSocketDisconnect, APIRouter

from oremda.typing import IdType

from oremda.models import (
    WebsocketModel,
)

from server.context import context
from server.utils import unique_id


router = APIRouter()


@router.websocket("")
async def create_websocket(
    socket: WebSocket, session_id: IdType = Query(..., alias="sessionId")
):
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
