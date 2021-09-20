from fastapi import APIRouter
from fastapi_websocket_rpc import RpcMethodsBase, WebsocketRPCEndpoint

from oremda.typing import IdType, JSONType

from server.context import context, GlobalContext
import server


async def notify_clients(message: JSONType, session_id: IdType, context: GlobalContext):
    websocket_ids = context.session_websockets.get(session_id, set())
    for websocket_id in websocket_ids:
        websocket = context.websockets[websocket_id]
        await websocket.socket.send_json(message)


class RpcMethods(RpcMethodsBase):
    async def notify_clients(self, message: JSONType, session_id: IdType):
        await notify_clients(message, session_id, context)


async def on_connect(channel):
    server.pipeline_runner = channel  # type: ignore


router = APIRouter()

# Create an endpoint and load it with the methods to expose
endpoint = WebsocketRPCEndpoint(RpcMethods(), on_connect=[on_connect])
# add the endpoint to the router
endpoint.register_route(router, "")